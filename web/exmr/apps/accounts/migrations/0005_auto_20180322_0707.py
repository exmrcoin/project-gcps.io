# Generated by Django 2.0.2 on 2018-03-22 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20180322_0658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='date_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='date time'),
        ),
    ]