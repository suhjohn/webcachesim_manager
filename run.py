import subprocess

from multiprocessing import Process

import time


def start_db():
    # start db
    command = "sudo docker-compose up -d"
    res_str = subprocess.check_output(command, shell=True, stderr=None).decode("utf-8")
    return res_str


def start_server():
    command = "cd webcachesim_server; python manage.py runserver"
    subprocess.check_output(command, stderr=subprocess.DEVNULL, shell=True)


def start_frontend():
    command = "cd webcachesim_frontend; yarn dev"
    subprocess.check_output(command, stderr=subprocess.DEVNULL, shell=True)


start_db()
time.sleep(5)
p1 = Process(target=start_server)
p2 = Process(target=start_frontend)
p1.start()
p2.start()
p1.join()
p2.join()
