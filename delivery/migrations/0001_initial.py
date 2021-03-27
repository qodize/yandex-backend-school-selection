# Generated by Django 3.1.7 on 2021-03-22 14:28

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Courier',
            fields=[
                ('courier_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('courier_type', models.CharField(choices=[('foot', 'foot'), ('bike', 'bike'), ('car', 'car')], max_length=4)),
                ('regions', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
                ('working_hours', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=11), size=None)),
            ],
        ),
    ]