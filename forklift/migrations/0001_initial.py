# Generated by Django 4.2.10 on 2024-02-16 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='tracker_device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_id', models.CharField(max_length=15, unique=True)),
                ('vehicle_name', models.CharField(max_length=20)),
                ('device_model', models.CharField(max_length=20)),
                ('vehicle_id', models.CharField(max_length=20)),
                ('driver', models.CharField(max_length=20)),
                ('add_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]