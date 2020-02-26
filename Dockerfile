FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /webcachesim_manager
RUN mkdir /webcachesim_manager/task_config_dir
RUN mkdir /webcachesim_manager/webcachesim_server
WORKDIR /webcachesim_manager
COPY task_config_dir/ /webcachesim_manager/task_config_dir
COPY webcachesim_server/ /webcachesim_manager/webcachesim_server
RUN pip install -r webcachesim_server/requirements.txt
WORKDIR /webcachesim_manager/webcachesim_server