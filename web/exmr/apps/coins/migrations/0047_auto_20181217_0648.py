# Generated by Django 2.0.2 on 2018-12-17 06:48

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('coins', '0046_merge_20181207_0904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paybyname',
            name='expiry',
            field=models.DateTimeField(default=datetime.datetime(2019, 12, 17, 6, 48, 32, 566127, tzinfo=utc)),
        ),
    ]