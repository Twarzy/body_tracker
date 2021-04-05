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
    DashboardView,
    MeasureEditView,
    MeasureDeleteView,
)


urlpatterns = [

    path('', views.dashboard, name='dashboard'),
    path('all/', MeasureView.as_view(), name='dashboard-all'),
    path('measure/<str:user>/<int:pk>', MeasureDetailView.as_view(), name='measure-detail'),
    path('add/', MeasureCreateView.as_view(), name='measure-add'),
    path('measure/<str:user>/<int:pk>/edit', MeasureEditView.as_view(), name='measure-edit'),
    path('measure/<str:user>/<int:pk>/delete', MeasureDeleteView.as_view(), name='measure-delete'),
    path('export/', views.export_records, name='export'),

    # testing_panel
    path('test', views.testing_panel, name='testing-panel'),

    # old - delete in future
    # path('tracker/', views.tracker, name='tracker')
    # path('', DashboardView.as_view(), name='dashboard'),
]
