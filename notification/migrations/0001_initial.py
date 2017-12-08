# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-23 02:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('link', '0001_initial'),
        ('account', '0002_auto_20171123_0233'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50)),
                ('viewed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='account.Account')),
                ('post', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='link.Post')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_notifications', to='account.Account')),
            ],
        ),
    ]
