from multiprocessing import Process, Queue
from multiprocessing.dummy import Pool as ThreadPool

import os
import datetime
import time

import pytz
from django.db import transaction

import itertools

from collections import defaultdict

from .models import Task, RemoteHost, get_running_tasks, get_task_progress, \
    get_task_ids_running_status


def run_tasks():
    p = Process(target=transition_tasks)
    p.start()
    print(p.pid)


def transition_failed_to_running():

    pass

def transition_tasks():
    def _get_running_tasks(args):
        _hostname, _host_registered_running_tasks = args
        _running_tasks = get_running_tasks(_hostname)
        task_running_status = get_task_ids_running_status(
            _running_tasks, [_task.task_id for _task in _host_registered_running_tasks]
        )
        # _running_tasks might include tasks that are executed on the node separate from the runner.
        # we only fetch the ones that are result of registered tasks
        return len([val for val in task_running_status.values() if val]), task_running_status

    def _start_task(task):
        task.start()

    while True:
        try:
            with transaction.atomic():
                # transition tasks that are not running on active nodes to failed
                active_hosts = RemoteHost.objects.filter(is_active=True)
                hostname_to_host = {host.hostname: host for host in active_hosts}
                running_tasks = Task.objects.filter(status=Task.RUNNING)
                tasks_running_on_not_active = []
                for task in running_tasks:
                    if task.executing_host.id not in {host.id for host in active_hosts}:
                        task.status = Task.FAILED
                        tasks_running_on_not_active.append(task)
                Task.objects.bulk_update(tasks_running_on_not_active, ['status'])

                ## Start
                created_tasks = Task.objects.filter(status=Task.CREATED)
                running_tasks = Task.objects.filter(status=Task.RUNNING)
                failed_tasks = Task.objects.filter(status=Task.FAILED)

                host_curr_running_task_count = {}  # tasks currently running on host
                host_assigned_tasks_is_running = {}  # host : {<task_id>: true | false}
                host_registered_running_tasks = {host.hostname: [] for host in active_hosts}  # tasks grouped by hostname
                for task in running_tasks:
                    host_registered_running_tasks[task.executing_host.hostname].append(task)
                pool = ThreadPool(4)
                results = pool.map(_get_running_tasks, host_registered_running_tasks.items())
                pool.close()
                pool.join()
                for res, host in zip(results, active_hosts):
                    count, running_status = res
                    host_curr_running_task_count[host.hostname] = count
                    host_assigned_tasks_is_running[host.hostname] = running_status
                print(host_assigned_tasks_is_running)
                # running update to done or failed
                if running_tasks:
                    # Update progress
                    for host in active_hosts:
                        host_running_tasks = host_registered_running_tasks[host.hostname]
                        pool = ThreadPool(4)
                        results = pool.map(get_task_progress, host_running_tasks)
                        pool.close()
                        pool.join()
                        # Update Progress
                        for task, progress in zip(host_running_tasks, results):
                            if not progress or progress["status"] == "Created":  # exception returns empty dict
                                continue
                            task.total_count = progress["total_count"]
                            task.current_count = progress["current_count"]
                            task.count_per_second = int(progress["segment_window"] / progress["segment_time_taken"])
                            if progress["status"] == "Complete":
                                task.total_count = task.current_count  # hack to match actual total_count with the executed count

                    # Update task.status
                    for host in active_hosts:
                        host_running_tasks = host_registered_running_tasks[host.hostname]
                        for task in host_running_tasks:
                            if task.is_complete():
                                print(f"task {task.id} Done")
                                task.status = Task.DONE
                                task.completed_at = datetime.datetime.now(tz=pytz.UTC)
                                host_curr_running_task_count[host.hostname] -= 1
                            elif not task.is_complete() and host_assigned_tasks_is_running[host.hostname][task.task_id]:
                                # still running
                                pass
                            elif not task.is_complete() and not host_assigned_tasks_is_running[host.hostname][task.task_id]:
                                # not complete but no longer running
                                print(f"task {task.id} Failed")
                                task.status = Task.FAILED
                                host_curr_running_task_count[host.hostname] -= 1
                        Task.objects.bulk_update(
                            host_running_tasks,
                            ['total_count', 'current_count', 'count_per_second', 'status', 'completed_at']
                        )

                available_cores = {
                    host.hostname: host.capacity - host_curr_running_task_count[host.hostname]
                    for host in active_hosts
                }
                i = 0
                transitioned_tasks = []

                # failed to running
                for task in failed_tasks:
                    print(available_cores)
                    if not available_cores:
                        # no available cores to be scheduled currently
                        break
                    hostname = list(sorted(available_cores.keys()))[i % len(available_cores)]
                    available_cores[hostname] -= 1
                    if available_cores[hostname] == 0:
                        print(f"{hostname} exhausted all available cores.")
                        del available_cores[hostname]
                        i -= 1
                    task.executing_host = hostname_to_host[hostname]
                    transitioned_tasks.append(task)
                    print(f"Fail to Running: {task.task_id} assigned to {hostname}")
                    i += 1

                i = 0
                # created to running
                for task in created_tasks:
                    if not available_cores:
                        # no available cores to be scheduled currently
                        break
                    hostname = list(sorted(available_cores.keys()))[i % len(available_cores)]
                    available_cores[hostname] -= 1
                    if available_cores[hostname] == 0:
                        del available_cores[hostname]
                        i -= 1
                    task.executing_host = hostname_to_host[hostname]
                    transitioned_tasks.append(task)
                    print(f"Created to Running: {task.task_id} assigned to {hostname}")
                    i += 1

                pool = ThreadPool(4)
                results = pool.map(_start_task, transitioned_tasks)
                pool.close()
                pool.join()

                if transitioned_tasks:
                    for task in transitioned_tasks:
                        task.status = Task.RUNNING
                        task.started_at = datetime.datetime.now(tz=pytz.UTC)
                    Task.objects.bulk_update(transitioned_tasks, ['status', 'executing_host', 'started_at'])
                print("------------------------------------------")
        except Exception as e:
            print(e)
        time.sleep(10)

# if __name__ == '__main__':
#     queue = Queue()
#     p = Process(target=my_function, args=(queue, 1))
#     p.start()
#     p.join() # this blocks until the process terminates
#     result = queue.get()
#     print result
