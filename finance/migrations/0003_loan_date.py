# Generated by Django 4.0.1 on 2022-02-19 16:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_diposit_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]