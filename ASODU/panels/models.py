from django.db import models
from django.core.validators import RegexValidator

from users.models import User

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
    )
    created = models.DateField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ('name',)

    def __str__(self):
        return self.name
