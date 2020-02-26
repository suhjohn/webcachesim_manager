import re
import signal
from multiprocessing.pool import ThreadPool

import subprocess

from multiprocessing import Process

import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status

from .background_task import transition_tasks
from .serializers import CreatedTaskSerializer, TaskSerializer
from .models import Task, RemoteHost, get_running_tasks, get_task_ids_running_status
from django.conf import settings

import yaml


def cartesian_product(param: dict):
    worklist = [param]
    res = []

    while len(worklist):
        p = worklist.pop()
        split = False
        for k in p:
            if type(p[k]) == list:
                _p = {_k: _v for _k, _v in p.items() if _k != k}
                for v in p[k]:
                    worklist.append({
                        **_p,
                        k: v,
                    })
                split = True
                break

        if not split:
            res.append(p)

    return res


def generate_task_parameters(config_params, default_algorithm_params, trace_params):
    tasks = []
    for trace_file in config_params['trace_files']:
        for cache_type in config_params['cache_types']:
            for cache_size_or_size_parameters in trace_params[trace_file]['cache_sizes']:
                # element can be k: v or k: list[v], which would be expanded with cartesian product
                # priority: default < per trace < per trace per algorithm < per trace per algorithm per cache size
                parameters = {}
                if cache_type in default_algorithm_params:
                    parameters = {**parameters, **default_algorithm_params[cache_type]}
                per_trace_params = {}
                for k, v in trace_params[trace_file].items():
                    if k not in ['cache_sizes'] and k not in default_algorithm_params and v is not None:
                        per_trace_params[k] = v
                parameters = {**parameters, **per_trace_params}
                if cache_type in trace_params[trace_file]:
                    # trace parameters overwrite default parameters
                    parameters = {**parameters, **trace_params[trace_file][cache_type]}
                if isinstance(cache_size_or_size_parameters, dict):
                    # only 1 key (single cache size) is allowed
                    assert (len(cache_size_or_size_parameters) == 1)
                    cache_size = list(cache_size_or_size_parameters.keys())[0]
                    if cache_type in cache_size_or_size_parameters[cache_size]:
                        # per cache size parameters overwrite other parameters
                        parameters = {**parameters, **cache_size_or_size_parameters[cache_size][cache_type]}
                else:
                    cache_size = cache_size_or_size_parameters
                parameters_list = cartesian_product(parameters)
                for parameters in parameters_list:
                    task = {
                        'trace_file': trace_file,
                        'cache_type': cache_type,
                        'cache_size': cache_size,
                        **parameters,
                    }
                    for k, v in config_params.items():
                        if k not in [
                            'cache_types',
                            'trace_files',
                            'algorithm_param_file',
                            'trace_param_file',
                            'config_file',
                            'debug',
                            'nodes',
                        ] and v is not None:
                            task[k] = v
                    tasks.append(task)
    # check for duplicate tasks
    task_set = set()
    filtered_list = list()
    filtered_task_tuples = list()
    for task in tasks:
        # generate tuple of (k1, v1, k2, v2, ..., kn, vn)
        task_keys = sorted(task.keys())
        task_as_list = []
        for key in task_keys:
            task_as_list.append(key)
            task_as_list.append(task[key])
        unique_task_identifier = tuple(task_as_list)
        if unique_task_identifier in task_set:
            continue
        task_set.add(unique_task_identifier)
        filtered_list.append(task)
        filtered_task_tuples.append(task)
    return filtered_list


class DefaultConfigRetrieveView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        with open(settings.AUTHENTICATION_PARAM_FILE) as f:
            auth_params = {**yaml.load(f)}
        with open(settings.TASK_CONFIG_PARAM_FILE) as f:
            task_config_params = yaml.load(f)
            config_params = {**auth_params, **task_config_params}

        # load algorithm parameters
        with open(settings.ALGORITHM_PARAM_FILE) as f:
            algorithm_params = yaml.load(f)
        with open(settings.TRACE_PARAM_FILE) as f:
            trace_params = yaml.load(f)

        tasks = generate_task_parameters(config_params, algorithm_params, trace_params)
        return Response({"tasks": tasks}, status=status.HTTP_200_OK)


class DefaultNodesRetrieveView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            with open(settings.AUTHENTICATION_PARAM_FILE) as f:
                auth_params = {**yaml.load(f)}
            with open(settings.TASK_CONFIG_PARAM_FILE) as f:
                config_params = {**auth_params, **yaml.load(f)}

            hosts = []
            for node_config in config_params.get("nodes", []):
                host = re.search(r'\S*\@\S*', node_config).group(0)
                capacity = re.match(r'(?P<capacity>\d+)\/', node_config).group('capacity')
                if host:
                    hosts.append({"hostname": host, "capacity": capacity})

            return Response({"nodes": hosts}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"nodes":[], "exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        """
        """

        def _init_project(hostname):
            pass

        remote_hosts = request.data["remote_hosts"]
        remote_hosts_to_create = [RemoteHost(hostname=host["hostname"], capacity=host["capacity"], is_active=False)
                                  for host in remote_hosts]
        try:
            RemoteHost.objects.bulk_create(remote_hosts_to_create, ignore_conflicts=True)
            hostnames = [host.hostname for host in remote_hosts_to_create]
            created_remote_hosts = RemoteHost.objects.filter(hostname__in=hostnames)
            # Activate just created ones
            for host in created_remote_hosts:
                host.is_active = True
            RemoteHost.objects.bulk_update(created_remote_hosts, ['is_active'])
            # Deactivate the rest
            deactivate_hosts = RemoteHost.objects.exclude(hostname__in=hostnames)
            for host in deactivate_hosts:
                host.is_active = False
            RemoteHost.objects.bulk_update(deactivate_hosts, ['is_active'])

            return Response({}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class NodeRunningProcessView(APIView):
    """

    """

    def get(self, request):
        remote_hosts = RemoteHost.objects.filter(is_active=True).values_list("hostname")
        pool = ThreadPool(10)
        res = pool.map(get_running_tasks, remote_hosts)
        pool.close()
        pool.join()
        host_running_tasks = [
            {"hostname": remote_host, "tasks": resp}
            for remote_host, resp in zip(remote_hosts, res)
        ]
        return Response(host_running_tasks, status=status.HTTP_200_OK)

    def post(self, request):
        def _kill_webcachesim(hostname):
            command = f"ssh -y  {hostname} 'ps aux | grep webcachesim'"
            res_str = subprocess.check_output(command, shell=True, stderr=None, timeout=10).decode("utf-8")
            process_strs = [p for p in res_str.split("\n") if p and "grep" not in p]
            process_ids = []
            for process_str in process_strs:
                process_id = [row for row in process_str.split(" ") if row][1]
                process_ids.append(process_id)
            if process_ids:
                kill_command = f"ssh -y  {hostname} 'kill -9 {' '.join(process_ids)}'"
                subprocess.check_output(kill_command, shell=True, stderr=None)

        remote_host_names = request.data["remote_host_names"]
        pool = ThreadPool(10)
        pool.map(_kill_webcachesim, remote_host_names)
        pool.close()
        pool.join()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class NodeRepositoryView(APIView):
    def post(self, request):
        def _create_repo(hostname):
            command = f"ssh -y  {hostname} 'git clone https://suhjohn:{settings.GITHUB_KEY}@github.com/suhjohn/webcachesim.git; cd ~/webcachesim; ./setup.sh'"
            proc = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
            proc.wait()

        remote_host_names = request.data["remote_host_names"]
        pool = ThreadPool(10)
        pool.map(_create_repo, remote_host_names)
        pool.close()
        pool.join()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request):
        def _update_repo(hostname):
            command = f"ssh -y  {hostname} 'cd ~/webcachesim; git pull; ./setup.sh'"
            proc = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
            proc.wait()

        remote_host_names = request.data["remote_host_names"]
        pool = ThreadPool(10)
        pool.map(_update_repo, remote_host_names)
        pool.close()
        pool.join()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


status_qp_to_model = {
    "created": Task.CREATED,
    "running": Task.RUNNING,
    "done": Task.DONE,
    "failed": Task.FAILED
}


# Create your views here.

class TaskListCreateView(APIView):
    """
    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request, format=None):
        """
        """
        tasks = request.data["tasks"]
        tasks_to_create = list()
        for task_parameters in tasks:
            task_id = Task.get_hash(task_parameters)
            tasks_to_create.append(Task(task_id=task_id, parameters=task_parameters))
        try:
            Task.objects.bulk_create(tasks_to_create, ignore_conflicts=True)
            return Response({}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        status_to_filter = request.query_params.get("status", "created")
        if status_to_filter not in status_qp_to_model:
            raise Exception
        tasks = Task.objects.filter(status=status_qp_to_model[status_to_filter])
        if status_to_filter == "created":
            serializer = CreatedTaskSerializer(tasks, many=True)
            data = serializer.data
        else:
            serializer = TaskSerializer(tasks, many=True)
            data = serializer.data
        return Response({"tasks": data}, status=status.HTTP_200_OK)


class TaskAutomaticExecutionView(APIView):
    AUTOMATIC_PROCESS_ID = -1
    AUTOMATIC_PROCESS_ON = False

    def get(self, request):
        return Response({"state": TaskAutomaticExecutionView.AUTOMATIC_PROCESS_ON}, status=status.HTTP_200_OK)

    def post(self, request):
        on = request.data["state"]
        assert isinstance(on, bool)
        if on != TaskAutomaticExecutionView.AUTOMATIC_PROCESS_ON:
            if TaskAutomaticExecutionView.AUTOMATIC_PROCESS_ID != -1:
                os.kill(TaskAutomaticExecutionView.AUTOMATIC_PROCESS_ID, signal.SIGKILL)
            if on:
                p = Process(target=transition_tasks)
                p.start()
                TaskAutomaticExecutionView.AUTOMATIC_PROCESS_ID = p.pid
            TaskAutomaticExecutionView.AUTOMATIC_PROCESS_ON = on
        return Response({}, status=status.HTTP_204_NO_CONTENT)
