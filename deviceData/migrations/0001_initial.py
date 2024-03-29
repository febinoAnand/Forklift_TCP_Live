# Generated by Django 4.2.10 on 2024-02-16 07:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('forklift', '0002_alter_tracker_device_driver_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GPS_Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=7, default=0.0, max_digits=10)),
                ('longitude', models.DecimalField(decimal_places=7, default=0.0, max_digits=10)),
                ('distance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('speed', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('state', models.IntegerField(choices=[(1, 'Inactive'), (2, 'Idle'), (3, 'Active')])),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('device_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forklift.tracker_device')),
            ],
        ),
    ]
