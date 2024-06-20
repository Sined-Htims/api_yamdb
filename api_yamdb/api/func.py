import random
import string

from django.core.mail import send_mail


# Для себя
def get_code():
    """Функция для гкнирирования кода подтверждения"""
    # Диапазоны кодов ASCII для цифр, заглавных и строчных букв
    digits = string.digits
    uppercase_letters = string.ascii_uppercase
    lowercase_letters = string.ascii_lowercase
    # Объединяем все диапазоны символов в один список
    all_chars = digits + uppercase_letters + lowercase_letters
    # Генерируем случайную последовательность из 10 символов
    code = ''.join(random.choice(all_chars) for _ in range(10))
    return code


def send_mail_with_code(email, token):
    send_mail(
        subject='Код подтверждения',
        message=f'Ваш код подтверждения на регистрацию: {token}',
        from_email='from@example.com',
        recipient_list=[email],
        fail_silently=False,
    )
