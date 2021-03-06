# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-04 23:08
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('abreviation', models.CharField(max_length=5, verbose_name='abreviation')),
            ],
        ),
        migrations.CreateModel(
            name='ProbabilityCurve',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alpha', models.FloatField(verbose_name='alpha')),
                ('betha', models.FloatField(verbose_name='betha')),
                ('kappa', models.FloatField(verbose_name='kappa')),
                ('distribution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats.Distribution', verbose_name='distribution')),
            ],
        ),
        migrations.CreateModel(
            name='ReducedSerie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temporal_serie_id', models.IntegerField(verbose_name='temporal serie id')),
                ('limiar', models.FloatField(null=True, verbose_name='limiar')),
                ('discretization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Discretization', verbose_name='discretization')),
                ('original_serie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.OriginalSerie', verbose_name='original serie')),
            ],
            options={
                'verbose_name': 'Reduced Serie',
                'verbose_name_plural': 'Reduced Series',
            },
        ),
        migrations.CreateModel(
            name='Reduction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=20, verbose_name='type')),
                ('type_en_us', models.CharField(max_length=20, null=True, verbose_name='type')),
                ('type_pt_br', models.CharField(max_length=20, null=True, verbose_name='type')),
                ('hydrologic_year_type', models.CharField(choices=[('flood', 'flood'), ('drought', 'drought')], max_length=50, verbose_name='hydrologic year type')),
                ('stats_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Stats', verbose_name='stats type')),
            ],
            options={
                'verbose_name': 'Reduction',
                'verbose_name_plural': 'Reductions',
            },
        ),
        migrations.CreateModel(
            name='ResamplingSerie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('length', models.IntegerField(verbose_name='length')),
                ('data', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None, verbose_name='data')),
                ('probabilities', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, size=None, verbose_name='probabilities')),
                ('is_base_curve', models.BooleanField(verbose_name='Is base curve')),
                ('curve', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats.ProbabilityCurve', verbose_name='curve')),
            ],
        ),
        migrations.AddField(
            model_name='reducedserie',
            name='reduction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats.Reduction', verbose_name='reduction'),
        ),
    ]
