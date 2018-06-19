# Generated by Django 2.0.2 on 2018-06-19 09:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coins', '0022_newcoin_vote_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coinvote',
            name='coin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coins.NewCoin', verbose_name='coin'),
        ),
        migrations.AlterField(
            model_name='newcoin',
            name='token_name',
            field=models.CharField(max_length=10, unique=True, verbose_name='token name'),
        ),
    ]