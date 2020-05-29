# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2020-05-29 01:28
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('eox_tagging', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='belongs_to_object_id',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='tag',
            name='belongs_to_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='belongs_to_tag_type', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='tag',
            name='tagged_object_id',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='tag',
            name='tagged_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='tag_type', to='contenttypes.ContentType'),
        ),
    ]
