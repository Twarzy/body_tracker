from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeDoneView
from .forms import (UserRegisterForm,
                    UserUpdateForm,
                    ProfileUpdateForm,
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
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

#TODO BUG - if u_form is not valied (username already taken) p_form is overwrite profile model as blank

        if u_form.is_valid():
            u_form.save()
            messages.success(request, 'Your account has been changed')
            return redirect('profile')


        elif p_form.is_valid():
            p_form.save()
            messages.success(request, 'Your profile details has been updated')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    activated = request.GET.get('change')

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'activated': activated
    }

    return render(request, 'users/profile.html', context)


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
