import os
import shutil

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from .constants import FUNCTION_TYPE_CHOICES, UNITS_CHOICES
from panels.utils import transliterate
from users.models import User


class DeletableObject(models.Model):
    is_deleted = models.BooleanField(
        'Удален из просмотра пользователями',
        default=False,
    )
    date_deleted = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.is_deleted and not self.date_deleted:
            self.date_deleted = timezone.now()
        elif not self.is_deleted:
            self.date_deleted = None
        super().save(*args, **kwargs)


class Vendor(models.Model):
    name = models.CharField(
        max_length=254,
        blank=False,
        null=False,
        verbose_name='Завод изготовитель',
        help_text='Введите название',
    )

    class Meta:
        verbose_name = 'Вендор'
        verbose_name_plural = 'Вендоры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(
        max_length=254,
        blank=False,
        null=False,
        verbose_name='Название',
        validators=[
            RegexValidator(
                inverse_match=True,
                message='В названии необходимо использовать буквы.',
                regex='^[0-9\\W]+$',
                code='invalid_name')
        ],
        unique=True,
        help_text='Введите название проекта',
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Описание',
        help_text='Добавьте краткое описание',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Автор',
        related_name='projects',
    )
    is_published = models.BooleanField(
        'Флаг общего доступа',
        help_text='Открыть доступ для просмотра всем',
        default=True,
    )
    co_authors = models.ManyToManyField(
        User,
        verbose_name='Соавторы',
        blank=True,
        related_name='co_projects'
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ('-created',)

    def delete(self, *args, **kwargs):
        storage_dir = os.path.join(
            settings.MEDIA_ROOT,
            'panels',
            f'{self.pk}',
        )
        if os.path.exists(storage_dir):
            shutil.rmtree(storage_dir)

        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name


class EquipmentGroup(models.Model):
    title = models.CharField(
        verbose_name='Название подгруппы оборудования',
        blank=False,
        null=False,
        default='Прочее',
        max_length=200
    )
    slug = models.SlugField(unique=True)
    description = models.TextField()

    class Meta():
        verbose_name = 'Группа оборудования'
        verbose_name_plural = 'Группы оборудования'
        ordering = ('title',)

    def __str__(self):
        return self.title


class Equipment(models.Model):
    description = models.TextField(
        max_length=500,
        blank=False,
        null=False,
        verbose_name='Наименование, техническая характеристика',
        help_text='Добавьте описание оборудования.',
        default='Оборудование в щите',
    )
    code = models.CharField(
        max_length=128,
        blank=False,
        null=False,
        verbose_name='Артикул/код оборудования',
        help_text='Введите артикул/код оборудования',
        unique=True,
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        verbose_name='Производитель',
        blank=False,
        null=False,
    )
    group = models.ForeignKey(
        EquipmentGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name='Группа оборудования',
    )
    units = models.CharField(
        max_length=64,
        choices=UNITS_CHOICES,
        default='шт.',
        verbose_name='Единицы измерения для спецификации'
    )

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'
        ordering = ('code',)

    def __str__(self):
        return f'{self.group} - {self.code} - {self.description[:80]}'


def get_storage_path(instance, filename):
    return os.path.join(
        'panels',
        f'{instance.panel.project.pk}',
        f'{instance.panel.pk}_{transliterate(instance.panel.name)}',
        filename
    )


class Attachment(models.Model):
    drawing = models.FileField(
        upload_to=get_storage_path,
        null=False,
        blank=False,
        verbose_name='Файл',
        help_text='Загрузите файл'
    )
    panel = models.ForeignKey(
        'Panel',
        null=False,
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    description = models.CharField(
        max_length=256,
        blank=False,
        null=True,
        verbose_name='Наименование чертежа',
        help_text='Добавьте краткое описание файла',
        default='Чертеж',
    )

    class Meta:
        verbose_name = 'Приложение'
        verbose_name_plural = 'Приложения'
        ordering = ('drawing',)

    def delete(self, *args, **kwargs):
        if self.drawing:
            file_path = self.drawing.path
            if os.path.exists(file_path):
                os.remove(file_path)

        super().delete(*args, **kwargs)

    def __str__(self):
        return self.drawing.name


class Panel(models.Model):
    name = models.CharField(
        max_length=64,
        blank=False,
        null=False,
        verbose_name='Название щита',
        help_text='Введите название щита',
        default='ЩА-00',
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name='Проект',
        related_name='panels',
    )
    function_type = models.CharField(
        max_length=64,
        choices=FUNCTION_TYPE_CHOICES,
        default='general',
        verbose_name='Функциональное назначение',
    )
    description = models.TextField(
        max_length=500,
        blank=False,
        null=False,
        verbose_name='Наименование, техническая характеристика',
        help_text='Добавьте описание щита.',
        default='Щит автоматизации общего назначения',
    )
    equipment = models.ManyToManyField(
        Equipment,
        verbose_name='Оборудование в щите',
        through='EquipmentPanelAmount',
    )
    files = models.ManyToManyField(
        Attachment,
        blank=True,
        verbose_name='Файлы',
        help_text='Загрузите схемы.',
        related_name='panels',
    )

    class Meta:
        verbose_name = 'Щит'
        verbose_name_plural = 'Щиты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'name'],
                name='unique_panel_in_project',
                violation_error_message=(
                    'Имя щита должно быть уникальным в проекте'),
            )
        ]

    def delete(self, *args, **kwargs):
        for attachment in self.attachments.all():
            attachment.delete()
        storage_dir = os.path.join(
            settings.MEDIA_ROOT,
            'panels',
            f'{self.project.pk}',
            f'{self.pk}_{transliterate(self.name)}',
        )
        if os.path.exists(storage_dir):
            shutil.rmtree(storage_dir)

        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name


class EquipmentPanelAmount(models.Model):
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        verbose_name='Оборудование',
    )
    panel = models.ForeignKey(
        Panel,
        on_delete=models.CASCADE,
        related_name='amounts',
    )
    amount = models.PositiveIntegerField(
        blank=False,
        null=False,
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                limit_value=1,
                message='Должно быть больше 0'
            )
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['equipment', 'panel'],
                name='unique_equipment_in_panel',
            )
        ]
        verbose_name = verbose_name_plural = 'Оборудование'
        ordering = ('equipment__group', 'equipment__code')

    def __str__(self):
        return str(self.equipment.group)
