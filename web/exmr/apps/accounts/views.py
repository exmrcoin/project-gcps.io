from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from Website.exmr.apps.accounts.forms import SignUpForm
from django.views.generic import View
class SignUp(View):
    def post(self, request):
        # if request.method == 'POST':
        #     form = SignUpForm(request.POST)
        #     if form.is_valid():
        #         form.save()
        #         email = form.cleaned_data.get('email')
        #         raw_password = form.cleaned_data.get('password1')
        #         User.objects.create_user(email=email, password=raw_password)
        #         user, created = User.objects.get_or_create(username=email, email=None)
        #         if created:
        #             user.set_password(raw_password)  # This line will hash the password
        #
        #             user.save()
        #         login(request, user)
        #         return redirect('home')
        #     else:
        #         print(form.errors)
        #         form = UserCreationForm()
        #     return render(request, 'signup.html', {'form': form})
        return HttpResponse('success')