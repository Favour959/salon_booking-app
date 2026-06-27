"""Send a single test email and report exactly what happens.

Usage (PowerShell/bash on Windows), all on one line:

    DJANGO_SECRET_KEY=x \
    DJANGO_EMAIL_BACKEND=anymail.backends.brevo.EmailBackend \
    BREVO_API_KEY=xkeysib-yourkey \
    "DJANGO_DEFAULT_FROM_EMAIL=Fav_hie's GlowUp Salon <oguadinmafavour@gmail.com>" \
    venv/Scripts/python.exe manage.py send_test_email oguadinmafavour@gmail.com

It prints the backend in use and either SUCCESS or the full provider error
(e.g. "sender not verified", "invalid API key").
"""
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Send a test email to verify the email backend / Brevo setup.'

    def add_arguments(self, parser):
        parser.add_argument('recipient', help='Address to send the test to.')

    def handle(self, *args, **options):
        to = options['recipient']

        self.stdout.write(f'EMAIL_BACKEND   = {settings.EMAIL_BACKEND}')
        self.stdout.write(f'DEFAULT_FROM    = {settings.DEFAULT_FROM_EMAIL}')
        key = settings.ANYMAIL.get('BREVO_API_KEY', '')
        self.stdout.write(
            'BREVO_API_KEY   = '
            + (f'set ({key[:10]}…)' if key else 'NOT SET')
        )
        self.stdout.write(f'Sending to      = {to}\n')

        msg = EmailMultiAlternatives(
            subject='GlowUp Salon — test email',
            body='If you can read this, your email backend works.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to],
        )
        msg.attach_alternative(
            '<h2 style="color:#C06C84;">It works!</h2>'
            '<p>Your GlowUp Salon email backend is configured correctly.</p>',
            'text/html',
        )

        try:
            sent = msg.send(fail_silently=False)
        except Exception as exc:  # surface the real provider error
            raise CommandError(f'SEND FAILED: {type(exc).__name__}: {exc}')

        if sent:
            self.stdout.write(self.style.SUCCESS(
                f'SUCCESS — {sent} message handed to the provider. '
                'Check the inbox (and spam).'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                'Backend returned 0 — nothing was sent.'
            ))
