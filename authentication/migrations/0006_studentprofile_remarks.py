# Generated by Django 5.1.7 on 2025-03-30 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_teacherprofile_is_suspended'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='remarks',
            field=models.TextField(blank=True, null=True),
        ),
    ]
