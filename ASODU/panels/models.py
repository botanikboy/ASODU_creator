from django.db import models
from django.core.validators import RegexValidator, MinValueValidator

from users.models import User
from .constants import FUNCTION_TYPE_CHOICES, UNITS_CHOICES


class Vendor(models.Model):
    name = models.CharField(
        max_length=64,
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
        help_text='Введите название проекта.',
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Описание',
        help_text='Добавьте краткое описание проекта.',
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

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ('-created',)

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
