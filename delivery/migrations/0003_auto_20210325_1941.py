# Generated by Django 3.1.7 on 2021-03-25 14:41

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0002_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_hours',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=11), size=None),
        ),
    ]
