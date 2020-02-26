from django.urls import path

from . import views

urlpatterns = [
    path('config/', views.DefaultConfigRetrieveView.as_view(), name='config'),
    path('nodes/', views.DefaultNodesRetrieveView.as_view(), name='nodes'),
    path('nodes/process/', views.NodeRunningProcessView.as_view(), name='nodes'),
    path('nodes/repository/', views.NodeRepositoryView.as_view(), name='nodes'),
    path('automatic/', views.TaskAutomaticExecutionView.as_view(), name='task_automatic'),
    path('', views.TaskListCreateView.as_view(), name='task'),
]

