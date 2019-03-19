import string
import time
import datetime
import logging
import json
import redis

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.core.mail import EmailMessage, EmailMultiAlternatives

from celery import shared_task
from celery.utils.log import get_task_logger, logger

from apps.accounts.models import Profile

from datetime import datetime,timedelta
from exmr import settings



logger = get_task_logger(__name__)
redis_object = redis.StrictRedis(host='localhost',
	port='6379',
	password='',
	db=0, charset="utf-8", decode_responses=True)


# @shared_task
def send_newsletter(self, request, queryset):
    queryset.update(is_active=True)
    profiles = Profile.objects.filter(is_subscribed=True)
    print(profiles)
    for q in queryset:
        subject = q.subject
        content = q.content
        from_email = settings.EMAIL_HOST_USER
    if profiles:
        for profile in profiles:
            email = profile.user.email
            msg = EmailMultiAlternatives(subject, '', from_email, [email])
            msg.attach_alternative(content, "text/html")
            msg.send()

