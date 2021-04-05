from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from .models import Measurement
from users.models import Profile
from .forms import MeasurementForm
from django.utils import timezone
from django.template.context_processors import csrf
import datetime, csv


# TODO Export data to various formats (csv, pdf, ?) API?
# TODO Progress chart in dashboard
# TODO User gallery (rather private)
# TODO MEASUREMENT url should be <username>/<date> format
# TODO BMI CALCULATOR for not logged user too
# TODO detailed add measurement (with lots of body part, BMI, water level, fat level)
# TODO BMI ANALYZER from profile
# TODO USER
# TODO Password recovery
# TODO Delete Account
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

        context = {'measures': [start_measure, latest_measure, changes, changes_perc],
                   'start': start_measure,
                   'now': latest_measure,
                   'changes': changes,
                   'perc': changes_perc,
                   'profile': user_profile
                   }

        return render(request, 'bst/dashboard.html', context)


# old unused - to delete in future
class DashboardView(MeasureView):
    template_name = 'bst/dashboard.html'

    def get_queryset(self):
        return Measurement.objects.filter(user=self.request.user).order_by('date')


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

    def test_func(self):
        measure = self.get_object()
        if self.request.user == measure.user:
            return True
        return False


# Editing measurements
class MeasureEditView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Measurement
    fields = ['weight', 'chest', 'waist', 'biceps']
    success_message = "Day %(date)s edited."

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            date=self.object.date,
        )

    def get_success_url(self):
        return reverse('dashboard-all')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        measure = self.get_object()
        if self.request.user == measure.user:
            return True
        return False


# TODO calendar view, with active links to "measure days" and disable for days without entered measurement


# Delete measurement
class MeasureDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Measurement

    # TODO add success message (SuccessMessageMixin not working on DeleteView)

    def get_success_url(self):
        return reverse('dashboard-all')

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

            writer = csv.writer(response)


            return response
        else:
            spam='sorry PDF file not supported yet'

            # spam = request.POST.getlist('file-format')
            context = {'spam': spam}
            return render(request, 'bst/export.html', context)


    return render(request, 'bst/export.html')




# Utilities

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
    return render(request, 'bst/test.html')


# just for testing on early development
def testing_panel(request):
    tracks = Measurement.objects.filter(user=request.user).order_by('date')

    context = {'tracks': tracks,
               }

    tracks = Measurement.objects.filter(user=request.user).order_by('date')
    start_measure = Measurement.objects.filter(user=request.user).order_by('date').first()
    latest_measure = Measurement.objects.filter(user=request.user).order_by('date').last()

    if not start_measure:
        return render(request, 'bst/panel.html')

    else:

        def percentage(first, last):
            result = (last / first - 1) * 100
            return round(result, 1)

        days_change = (latest_measure.date - start_measure.date).days
        weight_change = percentage(start_measure.weight, latest_measure.weight)
        chest_change = percentage(start_measure.chest, latest_measure.chest)
        waist_change = percentage(start_measure.waist, latest_measure.waist)
        biceps_change = percentage(start_measure.biceps, latest_measure.biceps)

        changes = {'date': days_change,
                   'weight': weight_change,
                   'chest': chest_change,
                   'waist': waist_change,
                   'biceps': biceps_change
                   }

        context = {'spams': [start_measure, latest_measure, changes]
                   }

        return render(request, 'bst/panel.html', context)
