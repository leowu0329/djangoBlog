from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.shortcuts import redirect
from .forms import CustomUserCreationForm


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


