# Generated by Django 3.0.3 on 2020-02-22 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_auto_20200222_0812'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='remotehost',
            name='host',
        ),
        migrations.AddField(
            model_name='remotehost',
            name='hostname',
            field=models.CharField(default='', max_length=2000, unique=True),
            preserve_default=False,
        ),
    ]
