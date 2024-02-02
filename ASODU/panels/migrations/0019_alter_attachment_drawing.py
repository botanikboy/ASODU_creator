# Generated by Django 4.2 on 2024-02-01 13:17

from django.db import migrations, models
import panels.models


class Migration(migrations.Migration):

    dependencies = [
        ('panels', '0018_alter_attachment_drawing_alter_attachment_panel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='drawing',
            field=models.FileField(help_text='Загрузите файл', upload_to=panels.models.get_storage_path, verbose_name='Файл'),
        ),
    ]