# Generated by Django 5.1.7 on 2025-04-02 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0004_attendance_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='time',
            field=models.TimeField(auto_now=True),
        ),
    ]
