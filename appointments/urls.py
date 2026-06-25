from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import StyledPasswordResetForm, StyledSetPasswordForm

urlpatterns = [
    path('',
         views.home,
         name='home'),

    path('register/',
         views.register_view,
         name='register'),

    path('login/',
         views.login_view,
         name='login'),

    path('logout/',
         views.logout_view,
         name='logout'),

    path('services/',
         views.services_view,
         name='services'),

    path('services/<int:pk>/',
         views.service_detail,
         name='service_detail'),

    path('book/<int:service_pk>/<int:staff_pk>/',
         views.book_appointment,
         name='book_appointment'),

    path('my-appointments/',
         views.my_appointments,
         name='my_appointments'),

    path('cancel/<int:pk>/',
         views.cancel_appointment,
         name='cancel_appointment'),

    path('staff/dashboard/',
         views.staff_dashboard,
         name='staff_dashboard'),

    # ── PASSWORD RESET (forgot password) ──────────
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='appointments/auth/password_reset_form.html',
             email_template_name='appointments/auth/password_reset_email.html',
             subject_template_name='appointments/auth/password_reset_subject.txt',
             form_class=StyledPasswordResetForm,
             success_url=reverse_lazy('password_reset_done'),
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='appointments/auth/password_reset_done.html',
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='appointments/auth/password_reset_confirm.html',
             form_class=StyledSetPasswordForm,
             success_url=reverse_lazy('password_reset_complete'),
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='appointments/auth/password_reset_complete.html',
         ),
         name='password_reset_complete'),
]