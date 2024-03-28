"""
URL configuration for telemedApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from health.views import *

urlpatterns = [
    path('send_prescription/', send_prescription, name='send_prescription'),
    path('period_history/', period_history, name='period_history'),
    path('ashaworker_update_link/', ashaworker_update_link, name='ashaworker_update_link'),
    path('prediction_result/', prediction_result, name='prediction_result'),
    path('ashaworker_appointments/', ashaworker_appointments, name='ashaworker_appointments'),
    path('appointment_booking/', appointment_booking, name='appointment_booking'),
    path('user_vc/', user_vc, name='user_vc'),
    path('prediction_input/', prediction_input, name='prediction_input'),
    path('mc_tracking/', mc_tracking, name='mc_tracking'),
    path('user_ashaworkers/', user_ashaworkers, name='user_ashaworkers'),
    path('doctor_todays_patient/', doctor_todays_patient, name='doctor_todays_patient'),
    path('appointments/', appointments, name='appointments'),
    path('poster4/', poster4, name='poster4'),
    path('poster3/', poster3, name='poster3'),
    path('poster2/', poster2, name='poster2'),
    path('poster1/', poster1, name='poster1'),
    path('predictive_analysis/', predictive_analysis, name='predictive_analysis'),
    path('educational_resources/', educational_resources, name='educational_resources'),
    path('patient_history/', patient_history, name='patient_history'),
    path('user_request_ashaworker/', user_request_ashaworker, name='user_request_ashaworker'),
    path('doctor_timeslot/', doctor_timeslot, name='doctor_timeslot'),
    path('doctor_dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('ashaworker_is_booking_appointment1/', ashaworker_is_booking_appointment1, name='ashaworker_is_booking_appointment1'),
    path('ashaworker_is_booking_appointment/', ashaworker_is_booking_appointment, name='ashaworker_is_booking_appointment'),
    path('ashaworker_dashboard/', ashaworker_dashboard, name='ashaworker_dashboard'),
    path('user_dashboard/', user_dashboard, name='user_dashboard'),
    path('logout_user/,', logout_user, name='logout_user'),
    path('home/', home, name='home'),
    path('logout_user/', logout_user, name='logout_user'),
    path('login_user/', login_user, name='login_user'),
    path('registration/', registration, name='registration'),
    path('admin/', admin.site.urls),
]
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
