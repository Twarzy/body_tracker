from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView
from bst.views import bmi_calculator
from bst.models import Measurement
from .models import Profile
from .forms import (UserRegisterForm,
                    UserUpdateForm,
                    ProfileEditForm,
                    )


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username} your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user.profile)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated')
            return redirect('profile')

    else:
        form = ProfileEditForm(instance=request.user.profile)
    profile_obj = Profile.objects.filter(user=request.user).first()

    latest_measure = Measurement.objects.filter(user=request.user).order_by('date').last()

    activated = request.GET.get('change')

    bmi = bmi_calculator(request.user)

    context = {
        'profile': profile_obj,
        'form': form,
        'activated': activated,
        'bmi': bmi
    }

    return render(request, 'users/profile.html', context)


@login_required
def change_account_details(request):

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile details has been updated')
            return redirect('profile')

    else:
        form = UserUpdateForm(instance=request.user)

    context = {
        'form': form
    }

    return render(request, 'users/account_details.html', context)


class PasswordChange(PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed.')
        return super().form_valid(form)
