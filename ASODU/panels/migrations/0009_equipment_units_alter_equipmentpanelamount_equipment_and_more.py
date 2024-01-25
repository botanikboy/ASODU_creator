# Generated by Django 4.2 on 2023-06-11 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('panels', '0008_alter_equipmentpanelamount_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='units',
            field=models.CharField(choices=[('шт.', 'штуки'), ('м', 'метры'), ('компл.', 'комплект'), ('упак.', 'упаковка')], default='шт.', max_length=64),
        ),
        migrations.AlterField(
            model_name='equipmentpanelamount',
            name='equipment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='panels.equipment', verbose_name='Оборудование'),
        ),
        migrations.AlterField(
            model_name='panel',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='panels', to='panels.project', verbose_name='Проект'),
        ),
    ]