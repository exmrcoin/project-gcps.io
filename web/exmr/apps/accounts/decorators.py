from django.urls import reverse
from django.shortcuts import redirect

from apps.accounts.models import Profile


def check_2fa(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            user_profile, created = Profile.objects.get_or_create(
                user=request.user)
            if not request.session.get('2fa_verified', False)\
            and not user_profile.two_factor_auth == 3 and not user_profile.two_factor_auth == 1:
                # redirect to verify authentication code
                return redirect(reverse('accounts:verify_2fa'))

        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap