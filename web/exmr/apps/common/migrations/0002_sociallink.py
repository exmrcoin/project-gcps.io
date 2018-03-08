# Generated by Django 2.0.2 on 2018-03-01 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(max_length=255, verbose_name='provider')),
                ('link', models.URLField(verbose_name='link')),
            ],
            options={
                'verbose_name': 'Social Link',
                'verbose_name_plural': 'Social Links',
            },
        ),
    ]
