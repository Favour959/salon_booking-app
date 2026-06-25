from django.db import models
from django.contrib.auth.models import User


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(
        upload_to='services/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class Staff(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff'
    )
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(
        upload_to='staff/',
        blank=True,
        null=True
    )
    specialties = models.ManyToManyField(
        Service,
        blank=True,
        related_name='staff_members'
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class TimeSlot(models.Model):
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='time_slots'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return (
            f"{self.staff} | {self.date} | "
            f"{self.start_time} - {self.end_time}"
        )

    class Meta:
        ordering = ['date', 'start_time']


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    time_slot = models.OneToOneField(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='appointment'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.client.username} → "
            f"{self.service.name} on "
            f"{self.time_slot.date}"
        )

    class Meta:
        ordering = ['-created_at']

# Create your models here.
