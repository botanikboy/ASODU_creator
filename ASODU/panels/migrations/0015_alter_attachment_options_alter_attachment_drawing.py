# Generated by Django 4.2 on 2024-01-31 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panels', '0014_remove_panel_attachments_attachment_panel_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attachment',
            options={'ordering': ('drawing',), 'verbose_name': 'Приложение', 'verbose_name_plural': 'Приложения'},
        ),
        migrations.AlterField(
            model_name='attachment',
            name='drawing',
            field=models.FileField(blank=True, help_text='Загрузите файл', null=True, upload_to='panels/'),
        ),
    ]