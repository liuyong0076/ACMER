# Generated by Django 3.0.2 on 2020-02-19 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acmerdata', '0021_contestforecast'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentcontest',
            name='endtimestamp',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='studentcontest',
            name='starttimestamp',
            field=models.IntegerField(default=0),
        ),
    ]