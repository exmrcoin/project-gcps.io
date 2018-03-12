import random
import string

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string


def generate_key(length):
    """
    Common util function that generates random string of desired length from set of letters and digits
    :param length:
    :return: random string
    """
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def send_email(subject, ctx_dict, to_email, email_template_txt=None, email_template_html=None, request=None):
    """
    Send an email utility
    """

    # Email subject *must not* contain newlines

    if type(to_email) == str:
        to_email = [to_email]
    subject = ''.join(subject.splitlines())

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
    message_txt = render_to_string(email_template_txt,
                                   ctx_dict, request=request)

    email_message = EmailMultiAlternatives(subject, message_txt,
                                           from_email, to_email)

    try:
        message_html = render_to_string(
            email_template_html, ctx_dict, request=request)
    except TemplateDoesNotExist:
        pass
    else:
        email_message.attach_alternative(message_html, 'text/html')

    email_message.send()
