from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (UserChangeForm, UserCreationForm,
                                       PasswordResetForm)
from django.template.loader import render_to_string

from .tasks import send_email_task

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email')


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta(UserChangeForm.Meta):
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
        ]


class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name, context,
                  from_email, to_email, html_email_template_name=None):
        subject_string = render_to_string(subject_template_name, context)
        subject = ''.join(subject_string.splitlines())
        body = render_to_string(email_template_name, context)
        html_message = (render_to_string(html_email_template_name, context)
                        if html_email_template_name else None)

        send_email_task.delay(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=[to_email],
            html_message=html_message
        )
