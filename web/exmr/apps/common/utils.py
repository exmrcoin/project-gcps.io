import random
import string
import gnupg

from django.conf import settings
from django.core.mail import send_mail as send_email_django
from django.utils.encoding import smart_text
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.http import JsonResponse
from apps.accounts.models import Profile

gpg = gnupg.GPG(gnupghome="gnupg")

def generate_key(length):
    """
    Common util function that generates random string of desired length from set of letters and digits
    :param length:
    :return: random string
    """
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def get_pin(length=6):
    """ Return a numeric PIN with length digits """
    pin = str(random.sample(range(10 ** (length - 1), 10 ** length), 1)[0])
    print("pin "+pin)

    return pin


def send_mail(user, subject, message, from_email, recipient_list, fail_silently=False,\
              auth_user=None, auth_password=None, connection=None, html_message=None):
    """
    Send an email utility
    """
    message = smart_text(gpg.sign(message))
    try:
        Profile.objects.get(user= user).pgp_gpg_public_key
        message = smart_text(gpg.encrypt(message))
    except:
        pass
    send_email_django(subject, message, from_email, recipient_list, fail_silently,\
              auth_user, auth_password, connection, html_message)
    return True

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

    message_html = render_to_string(
        email_template_html, ctx_dict, request=request)

    email_message.attach_alternative(message_html, 'text/html')

    email_message.send()
#     # Email subject *must not* contain newlines

#     if type(to_email) == str:
#         to_email = [to_email]
#     subject = ''.join(subject.splitlines())

#     from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
#     message_txt = render_to_string(email_template_txt,
#                                    ctx_dict, request=request)

#     email_message = EmailMultiAlternatives(subject, message_txt,
#                                            from_email, to_email)

#     message_html = render_to_string(
#         email_template_html, ctx_dict, request=request)

#     email_message.attach_alternative(message_html, 'text/html')

#     email_message.send()


class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context
