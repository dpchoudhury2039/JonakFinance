# Generated by Django 4.0.1 on 2022-02-19 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_loan_outstanding'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanrecovery',
            name='collectionPlace',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='premiumcollectionrecord',
            name='collectionPlace',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]