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
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from bst import views as bst_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', bst_views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('bst/', include('bst.urls')),
    path('contact/', bst_views.contact, name='contact'),
    path('bmi/', bst_views.bmi_calc, name='bmi'),
    path('', include('users.urls')),
    #  testing pages - to delete in future

    # path('test', bst_views.test, name='test'),
]
