import logging

from celery import shared_task
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_task(
    self, subject, message, from_email, recipient_list, html_message=None
):
    try:
        logger.info(
            'Начало выполнения задачи по отправке почты. '
            f'Попытка № {self.request.retries + 1}'
        )
        return send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
            html_message=html_message
        )
    except Exception as exc:
        logger.error(
            f'Ошибка отправки почты: {exc}. Повторная попытка...'
        )
        raise self.retry(exc=exc, countdown=10)
