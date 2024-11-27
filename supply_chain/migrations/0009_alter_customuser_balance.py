# Generated by Django 5.1.2 on 2024-10-24 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supply_chain', '0008_rename_token_balance_customuser_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=100000, max_digits=10),
        ),
    ]