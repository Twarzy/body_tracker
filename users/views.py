from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from bst.views import bmi_calculator
from bst.models import Measurement
from .models import Profile
from .forms import (UserRegisterForm,
                    UserUpdateForm,
                    ProfileEditForm,
                    )


def register(request):
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


class UserPasswordChangeDone(PasswordChangeDoneView):

    # TODO change this "fancy" massage to the one provided by django,
    # or skip passwordchangedone and leave just password change with added success
    # message after password change

    class SuccessMessage:
        tags = 'success'

        def __str__(self):
            return 'Password changed successfully'

    extra_context = {'messages': [SuccessMessage]}




# TODO profile, change photo, change password, maybe change username, change email
