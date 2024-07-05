from django.core.mail import send_mail


def send_mail_with_code(email, token):
    send_mail(
        subject='Код подтверждения',
        message=f'Ваш код подтверждения на регистрацию: {token}',
        from_email='from@example.com',
        recipient_list=[email],
        fail_silently=False,
    )
