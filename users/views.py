from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
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



def profile(request):

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user.profile)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated')
            return redirect('profile')

    else:
        form = ProfileEditForm(instance=request.user.profile)
    profile = Profile.objects.filter(user=request.user).first()

    activated = request.GET.get('change')

    context = {
        'profile': profile,
        'form': form,
        'activated': activated
    }

    return render(request, 'users/profile.html', context)

# def change_account_details(request):
    # if request.method == 'POST':
    #     u_form = UserUpdateForm(request.POST, instance=request.user)
    #     p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
    #
    #     # TODO BUG - if u_form is not valied (username already taken) p_form is overwrite profile model as blank
    #
    #     if not u_form.is_valid():
    #         messages.info(request, 'Error')
    #         return redirect('profile')
    #
    #     elif u_form.is_valid():
    #         if User.objects.filter(username=u_form.cleaned_data.get('username')).exists():
    #             messages.warning(request, 'Username Taken')
    #         else:
    #             u_form.save()
    #             messages.success(request, 'Your account has been changed')
    #         return redirect('profile')
    #
    #     if p_form.is_valid():
    #         p_form.save()
    #         messages.success(request, 'Your profile details has been updated')
    #         return redirect('profile')
    #
    # else:
    #     u_form = UserUpdateForm(instance=request.user)
    #     p_form = ProfileUpdateForm(instance=request.user.profile)
    #
    # activated = request.GET.get('change')
    #
    # context = {
    #     'u_form': u_form,
    #     'p_form': p_form,
    #     'activated': activated
    # }
    #
    # return render(request, 'users/profile.html', context)


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
