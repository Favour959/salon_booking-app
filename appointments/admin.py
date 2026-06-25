from django.contrib import admin
from .models import Service, Staff, TimeSlot, Appointment


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display  = ['name', 'duration_minutes', 'price']
    search_fields = ['name']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display  = ['__str__', 'user']
    search_fields = ['user__first_name', 'user__last_name']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display  = ['staff', 'date', 'start_time', 'end_time', 'is_available']
    list_filter   = ['staff', 'date', 'is_available']
    list_editable = ['is_available']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display  = ['client', 'service', 'staff', 'time_slot', 'status', 'created_at']
    list_filter   = ['status', 'staff', 'service']
    search_fields = ['client__username']
    list_editable = ['status']

# Register your models here.
