# Generated by Django 3.2.5 on 2021-12-04 02:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0004_alter_transaction_options'),
    ]

    operations = [
        migrations.DeleteModel(
            name='transaction',
        ),
    ]
