from django.contrib import admin
from .models import Task, RemoteHost


class TaskInline(admin.TabularInline):
    model = Task


class TaskAdmin(admin.ModelAdmin):
    search_fields = ('task_id', 'parameters')
    list_filter = ('status',)


class RemoteHostAdmin(admin.ModelAdmin):
    inlines = [
        TaskInline
    ]


admin.site.register(Task, TaskAdmin)
admin.site.register(RemoteHost, RemoteHostAdmin)
