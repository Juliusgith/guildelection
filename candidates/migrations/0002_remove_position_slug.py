# Generated by Django 5.0.2 on 2025-03-12 13:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='position',
            name='slug',
        ),
    ]
