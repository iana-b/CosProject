# Generated by Django 4.2.4 on 2023-08-15 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cosapp', '0005_alter_purchase_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='date',
            field=models.DateField(default='2023-08-15'),
            preserve_default=False,
        ),
    ]