# Generated by Django 5.0.2 on 2024-02-27 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('health', '0002_doctor_auth'),
    ]

    operations = [
        migrations.CreateModel(
            name='AshaWorker_Auth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('id_no', models.CharField(max_length=20)),
            ],
        ),
    ]
