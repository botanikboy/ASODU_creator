# Generated by Django 4.2 on 2023-04-23 15:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('panels', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vendor',
            options={'ordering': ('name',), 'verbose_name': 'Вендор', 'verbose_name_plural': 'Вендоры'},
        ),
    ]
