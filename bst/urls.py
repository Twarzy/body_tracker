"""body_tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from bst.views import (
    MeasureView,
    MeasureCreateView,
    MeasureDetailView,
    MeasureEditView,
    MeasureDeleteView,
    TestView,
)


urlpatterns = [

    path('', views.dashboard, name='dashboard'),
    path('add/', MeasureCreateView.as_view(), name='measure-add'),
    path('export/', views.export_records, name='export'),
    path('<username>/', MeasureView.as_view(), name='dashboard-all'),
    path('<username>/<slug:slug>', MeasureDetailView.as_view(), name='measure-detail'),
    path('<username>/<slug:slug>/edit', MeasureEditView.as_view(), name='measure-edit'),
    path('<username>/<slug:slug>/delete', MeasureDeleteView.as_view(), name='measure-delete'),



    # testing_panel
    # path('test', views.testing_panel, name='testing-panel'),
    path('test', TestView.as_view(), name='testing-panel'),
    ]