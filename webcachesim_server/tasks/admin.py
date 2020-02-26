from django.contrib import admin
from .models import Task, RemoteHost

class TaskAdmin(admin.ModelAdmin):
    pass

class RemoteHostAdmin(admin.ModelAdmin):
    pass

admin.site.register(Task, TaskAdmin)
admin.site.register(RemoteHost, RemoteHostAdmin)