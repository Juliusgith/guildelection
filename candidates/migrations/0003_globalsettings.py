# Generated by Django 5.0.6 on 2025-03-17 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0002_remove_position_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive', help_text='Enable or disable candidate applications globally.', max_length=20)),
            ],
            options={
                'verbose_name_plural': 'Global Settings',
            },
        ),
    ]
