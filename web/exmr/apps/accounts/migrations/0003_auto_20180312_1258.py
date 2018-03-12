# Generated by Django 2.0.2 on 2018-03-12 12:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0002_auto_20180301_1235'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileActivation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activation_key', models.CharField(max_length=64)),
                ('expired', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name_plural': 'Profile Activations',
                'verbose_name': 'Profile Activation',
            },
        ),
        migrations.AddField(
            model_name='profile',
            name='is_subscribed',
            field=models.BooleanField(default=False, verbose_name='is subscribed'),
        ),
    ]
