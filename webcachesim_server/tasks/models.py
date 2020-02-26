import json
import time
import hashlib
import re
import subprocess
from django.db import models
from django.contrib.postgres.fields import JSONField


def _get_task_identifier(task_params: dict):
    task_keys = sorted(task_params.keys())
    task_as_list = []
    for key in task_keys:
        task_as_list.append(key)
        task_as_list.append(task_params[key])
    unique_task_identifier = tuple(task_as_list)
    return unique_task_identifier


class RemoteHost(models.Model):
    hostname = models.CharField(max_length=2000, unique=True)
    capacity = models.IntegerField()
    is_active = models.BooleanField()

    def get_running_tasks(self):
        command = f"ssh {self.hostname} 'ps aux | grep webcachesim'"
        res_str = subprocess.check_output(command, shell=True, stderr=None, timeout=10).decode("utf-8")
        return list(set([val for val in re.findall(r'(?<=task_id )[a-zA-Z0-9_]+', res_str)]))


# Denotes the current state of the task
class Task(models.Model):
    CREATED = 0
    RUNNING = 1
    DONE = 2
    FAILED = -1

    STATUS_CHOICES = [
        (CREATED, 'Created'),  # if log["status"] "Created"
        (RUNNING, 'Running'),  # if task_is_running == True && log["status"] == "Running"
        (FAILED, 'Failed'),  # if task_is_running == False && log["status"] != "Running"
        (DONE, 'Done'),  # log["status"] "Done"
    ]

    task_id = models.CharField(max_length=256, null=False, unique=True)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=CREATED
    )
    parameters = JSONField()
    executing_host = models.ForeignKey(
        RemoteHost, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)

    # Values get updated as jobs are running
    total_count = models.BigIntegerField(null=True)
    current_count = models.BigIntegerField(null=True)
    count_per_second = models.BigIntegerField(null=True)

    @staticmethod
    def get_hash(parameters):
        unique_tuple = _get_task_identifier(parameters)
        h = hashlib.blake2s(digest_size=16)
        h.update(str(unique_tuple).encode())
        return h.hexdigest()

    @property
    def task_str(self):
        params = {}
        for k, v in self.parameters.items():
            if k not in ['trace_file', 'cache_type', 'cache_size'] and v is not None:
                params[k] = str(v)
        # use timestamp as task id
        params['task_id'] = self.task_id
        params = [f'{k} {v}' for k, v in params.items()]
        params = ' '.join(params)
        res = f'webcachesim_cli_v2 {self.parameters["trace_file"]} {self.parameters["cache_type"]} {self.parameters["cache_size"]} {params}'
        return res

    def start(self):
        if self.status == self.RUNNING:
            raise Exception
        command = f"nohup ssh {self.executing_host.hostname} '{self.task_str} > /dev/null 2>&1 &'"
        print(command)
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

    def is_complete(self):
        return self.total_count == self.current_count and self.total_count and self.current_count

    def update_running_status(self, total_count, current_count, count_per_second):
        self.total_count = total_count
        self.current_count = current_count
        self.count_per_second = count_per_second
        self.status = self.RUNNING
        self.save()

    def update_done_status(self, total_count, current_count, count_per_second):
        self.total_count = total_count
        self.current_count = current_count
        self.count_per_second = count_per_second
        self.status = self.DONE
        self.save()


# def task_is_running(task):
#     command = f"ssh -y  {task.host} 'ps aux | grep -i '{task.task_id}''"
#     proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
#     res = proc.stdout.read()
#     res_str = res.decode("utf-8")
#     res_arr = [line for line in res_str.split("\n") if line]
#     # hack: if process running, at least grep + current process will be returned.
#     return len(res_arr) > 2


def get_task_ids_running_status(running_tasks, task_ids):
    running_task_id_set = set(running_tasks)
    return {
        task_id: task_id in running_task_id_set
        for task_id in task_ids
    }


def get_running_tasks(hostname):
    command = f"ssh {hostname} 'ps aux | grep webcachesim'"
    res_str = subprocess.check_output(command, shell=True, stderr=None, timeout=10).decode("utf-8")
    return list(set([val for val in re.findall(r'(?<=task_id )[a-zA-Z0-9_]+', res_str)]))


def get_task_progress(task: Task):
    """
    ssh -y  ssuh@clnode170.clemson.cloudlab.us 'cat /tmp/log/webcachesim/tasklog/1582397590830'
    { "current_count" : 87000000, "total_count" : 2800000000, "segment_window" : 1000000,
    "segment_time_taken" : 0.74799999999999999822, "status" : "Running" }

    :param task:
    :return:
    """
    if task.parameters["cache_type"] == "Adaptive-TinyLFU":
        return {}
    command = f"ssh {task.executing_host.hostname} 'cat /tmp/log/webcachesim/tasklog/{task.task_id}'"
    try:
        res_str = subprocess.check_output(command, shell=True, stderr=None, timeout=10).decode("utf-8")
        task_status = json.loads(res_str)
        return task_status
    except Exception as e:
        print(e)
        print(task.id)
        return {}
