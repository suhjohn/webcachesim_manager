from rest_framework import serializers

from .models import Task


class CreatedTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task

        fields = ['status', 'parameters', 'created_at', 'task_id', 'id']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        depth = 1
        fields = [
            'id', 'status', 'parameters', 'created_at', 'task_id',
            'total_count', 'current_count', 'count_per_second', 'executing_host'
        ]
