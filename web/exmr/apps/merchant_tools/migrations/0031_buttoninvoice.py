# Generated by Django 2.0.2 on 2018-10-09 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchant_tools', '0030_auto_20181008_1239'),
    ]

    operations = [
        migrations.CreateModel(
            name='ButtonInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchant_id', models.CharField(max_length=128, verbose_name='merchant id')),
                ('invoice_number', models.CharField(max_length=128)),
                ('unique_id', models.CharField(max_length=128, unique=True)),
                ('item_name', models.CharField(max_length=128)),
                ('item_amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('item_number', models.CharField(max_length=128)),
                ('item_qty', models.DecimalField(decimal_places=2, max_digits=20)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=20, null=True)),
                ('shipping_cost', models.DecimalField(decimal_places=2, default=0, max_digits=20, null=True)),
                ('buyer_note', models.BooleanField(default=False)),
                ('first_name', models.CharField(max_length=128)),
                ('last_name', models.CharField(max_length=128)),
                ('email_addr', models.CharField(max_length=128)),
                ('addr_l1', models.CharField(max_length=128)),
                ('addr_l2', models.CharField(max_length=128)),
                ('country', models.CharField(max_length=128)),
                ('city', models.CharField(max_length=128)),
                ('state', models.CharField(max_length=128)),
                ('zipcode', models.CharField(max_length=128)),
                ('phone', models.CharField(max_length=128)),
                ('URL_link', models.CharField(max_length=256)),
            ],
        ),
    ]