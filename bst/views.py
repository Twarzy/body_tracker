from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext as _
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Measurement
from users.models import Profile
from .forms import MeasurementForm, BmiForm
import datetime, csv

# TODO Progress chart in dashboard - #IN PROGRESS
# TODO User gallery (rather private)
# TODO Improved BMI CALCULATOR
# TODO detailed add measurement (with lots of body part, BMI, water level, fat level)

# TODO calendar view, with active links to "measure days" and disable for days without entered measurement

# TODO USER
# TODO Password recovery
# TODO Different User profile details
# TODO height BMI (when adding measurement BMI should be auto evaluate and add to measurement table)
# TODO tracking water level/FAT in body


def home(request):
    return render(request, 'bst/home.html', context={'title': 'Home Page'})


# All user history
class MeasureView(LoginRequiredMixin, ListView):
    model = Measurement
    template_name = 'bst/dashboard_all.html'
    context_object_name = 'measures'

    def get(self, request, *args, **kwargs):

        # When user try to manually change username in url, he will be redirected to proper url
        if kwargs['username'] != self.request.user.username:
            return redirect('dashboard-all', self.request.user.username)

        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(_('Empty list and “%(class_name)s.allow_empty” is False.') % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()
        return self.render_to_response(context)

    # Display only logged user records
    def get_queryset(self):
        return Measurement.objects.filter(user=self.request.user).order_by('-date')


# Main dashboard view
@login_required
def dashboard(request):
    all_measure = Measurement.objects.filter(user=request.user).order_by('-date')
    start_measure = Measurement.objects.filter(user=request.user).order_by('date').first()
    latest_measure = Measurement.objects.filter(user=request.user).order_by('date').last()
    user_profile = Profile.objects.filter(user=request.user).first()

    # if some records are missing from latest measurement, it takes records from earlier one
    for rec in all_measure:
        if not latest_measure.weight:
            latest_measure.weight = rec.weight
        if not latest_measure.chest:
            latest_measure.chest = rec.chest
        if not latest_measure.waist:
            latest_measure.waist = rec.waist
        if not latest_measure.biceps:
            latest_measure.biceps = rec.biceps
        if latest_measure.weight and latest_measure.chest and latest_measure.waist and latest_measure.biceps:
            break

    if not start_measure:
        return render(request, 'bst/dashboard.html', {'profile': user_profile})
    else:
        changes_perc = {'date': (latest_measure.date - start_measure.date).days,
                        'weight': percentage(start_measure.weight, latest_measure.weight),
                        'chest': percentage(start_measure.chest, latest_measure.chest),
                        'waist': percentage(start_measure.waist, latest_measure.waist),
                        'biceps': percentage(start_measure.biceps, latest_measure.biceps)
                        }

        changes = {'date': (latest_measure.date - start_measure.date).days,
                   'weight': compare_two(latest_measure.weight, start_measure.weight),
                   'chest': compare_two(latest_measure.chest, start_measure.chest),
                   'waist': compare_two(latest_measure.waist, start_measure.waist),
                   'biceps': compare_two(latest_measure.biceps, start_measure.biceps)
                   }

        chart = {'labels': [],
                 'weight': [],
                 'chest': [],
                 'waist': [],
                 'biceps': []
                 }

        queryset = all_measure.reverse()
        for measure in queryset:
            chart['labels'].append(measure.date.strftime("%d.%m.%y"))

            for bodypart in ['weight', 'biceps', 'waist', 'chest']:
                chart[bodypart].append(getattr(measure, bodypart)) if getattr(measure, bodypart) else chart[
                    bodypart].append(chart[bodypart][-1]) if chart[bodypart][-1] else 0

        context = {'measures': [start_measure, latest_measure, changes, changes_perc],
                   'start': start_measure,
                   'now': latest_measure,
                   'changes': changes,
                   'perc': changes_perc,
                   'profile': user_profile,
                   'chart': chart
                   }

        return render(request, 'bst/test.html', context)


# Adding measurement
class MeasureCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Measurement
    form_class = MeasurementForm
    success_message = "Day %(date)s created."

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            date=self.object.date,
        )

    def get_success_url(self):
        return reverse('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user

        try:
            return super().form_valid(form)
        except IntegrityError:
            messages.warning(self.request, 'Measurement for that day is already added, '
                                           'change day, or try editing it in measurement history.')
            return redirect('measure-add')


# Single measurement view (not really using for now)
class MeasureDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Measurement
    slug_field = 'date'

    def get(self, request, *args, **kwargs):

        # When user try to manually change username in url, he will be redirected to proper url
        if kwargs['username'] != self.request.user.username:
            return redirect('measure-detail', self.request.user.username, kwargs['slug'])

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_queryset(self):
        return Measurement.objects.filter(user=self.request.user)

    def test_func(self):
        measure = self.get_object()
        if self.request.user == measure.user:
            return True
        return False


# Editing measurements
class MeasureEditView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Measurement
    slug_field = 'date'
    fields = ['weight', 'chest', 'waist', 'biceps']
    success_message = "Day %(date)s edited."

    def get(self, request, *args, **kwargs):

        # When user try to manually change username in url, he will be redirected to proper url
        if kwargs['username'] != self.request.user.username:
            return redirect('measure-edit', self.request.user.username, kwargs['slug'])

        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Measurement.objects.filter(user=self.request.user)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            date=self.object.date,
        )

    def get_success_url(self):
        return reverse('dashboard-all', args=[self.request.user])

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        measure = self.get_object()
        if self.request.user == measure.user:
            return True
        return False


# Delete measurement
class MeasureDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Measurement
    slug_field = 'date'

    def get(self, request, *args, **kwargs):

        # When user try to manually change username in url, he will be redirected to proper url
        if kwargs['username'] != self.request.user.username:
            return redirect('measure-delete', self.request.user.username, kwargs['slug'])

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        return self.render_to_response(context)

    def get_queryset(self):
        return Measurement.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.info(request, 'Measurement for {} deleted successfully.'.format(self.object.date))
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse('dashboard-all', args=[self.request.user])

    def test_func(self):
        measure = self.get_object()
        if self.request.user == measure.user:
            return True
        return False

# Export user measurements


def export_records(request):
    if request.method == 'POST':
        if request.POST.getlist('file-format')[0] == 'CSV':

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="BST_{}.csv"'.format(request.user)
            all_measure = Measurement.objects.filter(user=request.user).order_by('-date')
            fields = [field.name for field in get_model_fields(Measurement) if field.name not in ['id', 'user']]
            writer = csv.writer(response)
            writer.writerow(x.upper() for x in fields)

            for obj in all_measure:
                writer.writerow(getattr(obj, field) for field in fields)

            return response
    # TODO export user data in PDF format, rather html template to PDF
        else:
            messages.info(request, 'Sorry, PDF format not supported yet')
            return redirect('export')

    return render(request, 'bst/export.html')


def contact(request):
    return render(request, 'bst/contact.html')


def bmi_calc(request):

    if request.method == 'POST':
        form = BmiForm(request.POST)
        if form.is_valid():
            age = form.cleaned_data.get('age')
            gender = form.cleaned_data.get('gender')
            weight = form.cleaned_data.get('weight')
            height = form.cleaned_data.get('height')

            bmi = round(weight / (height / 100) ** 2, 1)

            context = {'form': form,
                       'bmi': bmi,
                       'bmi_analyse': bmi_analyzer(bmi)
            }

            return render(request, 'bst/bmi.html', context)

    else:
        form = BmiForm()

    return render(request, 'bst/bmi.html', {'form': form})


# Utilities

# need for export_records function
def get_model_fields(model):
    return model._meta.fields


def percentage(first, last):
    # Simple algorithm returning percentage change in two values
    if not first or not last:
        return '-'
    result = (last / first - 1) * 100
    return round(result, 1)


def compare_two(last, first):
    try:
        return last - first
    except TypeError:
        return '-'


def bmi_calculator(req_user):
    height, weight = None, None

    if Profile.objects.filter(user=req_user).first():
        height = Profile.objects.filter(user=req_user).first().height
    if Measurement.objects.filter(user=req_user).order_by('date').last():
        weight = Measurement.objects.filter(user=req_user).order_by('date').last().weight

    if height and weight:
        bmi = round(weight / (height / 100)**2, 1)
        return [bmi, bmi_analyzer(bmi)]


# Simple version for now, will be expanded later
def bmi_analyzer(bmi):

    category = 'Thinness' if bmi < 18.5 else 'Normal' if bmi < 25 else 'Overweight'
    return category


def test(request):
    pass


# just for testing on early development
def testing_panel(request):
    return render(request, 'bst/test.html')


class TestView(LoginRequiredMixin, ListView):
    model = Measurement
    template_name = 'bst/test.html'
    context_object_name = 'measures'

    # Display only logged user records
    def get_queryset(self):
        return Measurement.objects.filter(user=self.request.user).order_by('-date')
