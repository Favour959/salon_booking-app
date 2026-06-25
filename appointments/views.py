from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST
from .models import Service, Staff, Appointment, TimeSlot
from .forms import ClientRegistrationForm, AppointmentForm


# ── HOME ──────────────────────────────────────
def home(request):
    services     = Service.objects.all()
    staff_members = (
        Staff.objects
        .select_related('user')
        .prefetch_related('specialties')
    )
    return render(request, 'appointments/home.html', {
        'services':      services,
        'staff_members': staff_members,
    })


# ── REGISTER ──────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f'Welcome, {user.first_name}! Your account has been created.'
            )
            return redirect('home')
    else:
        form = ClientRegistrationForm()

    return render(request, 'appointments/register.html', {'form': form})


# ── LOGIN ─────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'appointments/login.html', {'form': form})


# ── LOGOUT ────────────────────────────────────
@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ── SERVICES LIST ─────────────────────────────
def services_view(request):
    services = Service.objects.all()
    return render(request, 'appointments/services.html', {
        'services': services
    })


# ── SERVICE DETAIL ────────────────────────────
def service_detail(request, pk):
    service         = get_object_or_404(Service, pk=pk)
    available_staff = Staff.objects.filter(specialties=service).select_related('user')
    return render(request, 'appointments/service_detail.html', {
        'service':         service,
        'available_staff': available_staff,
    })


# ── BOOK APPOINTMENT ──────────────────────────
@login_required
def book_appointment(request, service_pk, staff_pk):
    service = get_object_or_404(Service, pk=service_pk)
    staff   = get_object_or_404(Staff,   pk=staff_pk)

    # The staff member must actually offer this service.
    if not staff.specialties.filter(pk=service.pk).exists():
        messages.error(request, 'This stylist does not offer that service.')
        return redirect('service_detail', pk=service.pk)

    if request.method == 'POST':
        form = AppointmentForm(staff=staff, data=request.POST)
        if form.is_valid():
            chosen_slot = form.cleaned_data['time_slot']
            try:
                with transaction.atomic():
                    # Lock the row and re-check availability so two clients
                    # can't grab the same slot in a race.
                    slot = (
                        TimeSlot.objects
                        .select_for_update()
                        .get(pk=chosen_slot.pk, staff=staff, is_available=True)
                    )
                    # The slot is free, but a previously cancelled appointment
                    # may still be attached to it (time_slot is OneToOne).
                    # Clear it so the slot can be rebooked.
                    Appointment.objects.filter(
                        time_slot=slot, status='cancelled'
                    ).delete()

                    appointment         = form.save(commit=False)
                    appointment.client  = request.user
                    appointment.service = service
                    appointment.staff   = staff
                    appointment.time_slot = slot
                    appointment.save()

                    slot.is_available = False
                    slot.save(update_fields=['is_available'])
            except TimeSlot.DoesNotExist:
                messages.error(
                    request,
                    'Sorry, that time slot was just taken. Please pick another.'
                )
                return redirect('book_appointment',
                                service_pk=service.pk, staff_pk=staff.pk)

            messages.success(request, 'Appointment booked successfully!')
            return redirect('my_appointments')
    else:
        form = AppointmentForm(staff=staff)

    return render(request, 'appointments/book_appointment.html', {
        'form':    form,
        'service': service,
        'staff':   staff,
    })


# ── MY APPOINTMENTS ───────────────────────────
@login_required
def my_appointments(request):
    appointments = (
        Appointment.objects
        .filter(client=request.user)
        .select_related('service', 'staff__user', 'time_slot')
        .order_by('-created_at')
    )
    return render(request, 'appointments/my_appointments.html', {
        'appointments': appointments
    })


# ── CANCEL APPOINTMENT ────────────────────────
@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(
        Appointment, pk=pk, client=request.user
    )

    if appointment.status in ('cancelled', 'completed'):
        messages.error(request, 'This appointment cannot be cancelled.')
        return redirect('my_appointments')

    if request.method == 'POST':
        appointment.time_slot.is_available = True
        appointment.time_slot.save()
        appointment.status = 'cancelled'
        appointment.save()
        messages.warning(request, 'Your appointment has been cancelled.')
        return redirect('my_appointments')

    return render(request, 'appointments/cancel_confirm.html', {
        'appointment': appointment
    })


# ── STAFF DASHBOARD ───────────────────────────
@login_required
def staff_dashboard(request):
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        messages.error(request, 'You are not registered as a staff member.')
        return redirect('home')

    appointments = (
        Appointment.objects
        .filter(staff=staff)
        .exclude(status='cancelled')
        .select_related('client', 'service', 'time_slot')
        .order_by('time_slot__date', 'time_slot__start_time')
    )
    return render(request, 'appointments/staff_dashboard.html', {
        'staff':        staff,
        'appointments': appointments,
    })

# Create your views here.
