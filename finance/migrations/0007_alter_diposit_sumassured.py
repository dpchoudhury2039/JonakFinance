# Generated by Django 4.0.1 on 2022-02-20 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0006_alter_diposit_sumassured'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diposit',
            name='sumAssured',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
