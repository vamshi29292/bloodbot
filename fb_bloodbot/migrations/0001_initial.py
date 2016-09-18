# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-18 05:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BloodGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bloodGroup', models.CharField(max_length=5, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.FloatField(null=True)),
                ('lon', models.FloatField(null=True)),
                ('name', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=200, null=True)),
                ('recipient_ph_no', models.CharField(max_length=10)),
                ('bloodGroup', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fb_bloodbot.BloodGroup')),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fb_bloodbot.Location')),
            ],
        ),
        migrations.CreateModel(
            name='RhesusFactor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RhFactor', models.NullBooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('name', models.CharField(max_length=200)),
                ('gender', models.CharField(max_length=20, null=True)),
                ('fbId', models.CharField(max_length=200, primary_key=True, serialize=False, unique=True)),
                ('status', models.CharField(max_length=200)),
                ('last_donation', models.DateField(null=True)),
                ('bloodGroup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fb_bloodbot.BloodGroup')),
                ('rhesusFactor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fb_bloodbot.RhesusFactor')),
            ],
        ),
        migrations.AddField(
            model_name='request',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fb_bloodbot.User'),
        ),
        migrations.AddField(
            model_name='request',
            name='rhesusFactor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fb_bloodbot.RhesusFactor'),
        ),
        migrations.AddField(
            model_name='location',
            name='users',
            field=models.ManyToManyField(to='fb_bloodbot.User'),
        ),
    ]