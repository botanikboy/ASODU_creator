# Generated by Django 4.2 on 2024-01-31 06:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('panels', '0009_equipment_units_alter_equipmentpanelamount_equipment_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drawing', models.FileField(blank=True, help_text='Загрузите файл', null=True, upload_to='panels/', verbose_name='Чертёж')),
            ],
        ),
        migrations.AlterModelOptions(
            name='equipmentpanelamount',
            options={'ordering': ('equipment__group', 'equipment__code'), 'verbose_name': 'Оборудование', 'verbose_name_plural': 'Оборудование'},
        ),
        migrations.AlterField(
            model_name='equipment',
            name='units',
            field=models.CharField(choices=[('шт.', 'шт.'), ('м', 'м'), ('компл.', 'компл.'), ('упак.', 'упак.')], default='шт.', max_length=64, verbose_name='Единицы измерения для спецификации'),
        ),
        migrations.AlterField(
            model_name='equipmentpanelamount',
            name='panel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amounts', to='panels.panel'),
        ),
        migrations.AlterField(
            model_name='panel',
            name='function_type',
            field=models.CharField(choices=[('power', 'Силовой с локальной автоматикой'), ('automation', 'Локальная автоматика'), ('dispatch', 'Диспетчеризация'), ('room', 'Комнатная автоматика'), ('general', 'Общее назначение')], default='general', max_length=64, verbose_name='Функциональное назначение'),
        ),
        migrations.AddField(
            model_name='panel',
            name='attachements',
            field=models.ManyToManyField(help_text='Загрузите схемы.', to='panels.attachment', verbose_name='Файлы'),
        ),
    ]
