# Generated by Django 2.2.7 on 2019-11-11 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='bucket_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]