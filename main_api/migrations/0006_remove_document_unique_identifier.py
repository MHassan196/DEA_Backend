# Generated by Django 4.1.13 on 2024-02-12 17:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_api', '0005_document_unique_identifier'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='unique_identifier',
        ),
    ]