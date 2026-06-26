"""Appointment notification emails.

All sends use fail_silently=True so a mail problem (bad SMTP creds, provider
downtime) can never break booking or cancellation for the user.
"""
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def _format_when(appointment):
    slot = appointment.time_slot
    return (
        f"{slot.date:%A, %d %B %Y} at "
        f"{slot.start_time:%I:%M %p} – {slot.end_time:%I:%M %p}"
    )


def _send(subject, to_email, text_body, html_body):
    """Send one multipart (text + HTML) email. No-op if there's no address."""
    if not to_email:
        return
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(html_body, 'text/html')
    msg.send(fail_silently=True)


def _wrap_html(heading, lines, accent='#C06C84'):
    rows = ''.join(f'<p style="margin:4px 0;">{line}</p>' for line in lines)
    return f"""\
<div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;
            border:1px solid #f0e0e8;border-radius:12px;overflow:hidden;">
  <div style="background:linear-gradient(135deg,#1a0a12,#2d0f22);
              padding:20px 24px;">
    <span style="color:#fff;font-size:18px;font-weight:bold;">
      Fav_hie's <span style="color:{accent};">GlowUp</span> Salon
    </span>
  </div>
  <div style="padding:24px;color:#1a0a12;">
    <h2 style="color:{accent};margin-top:0;">{heading}</h2>
    {rows}
  </div>
  <div style="background:#fdf0f5;padding:14px 24px;font-size:12px;color:#8a7080;">
    This is an automated message from Fav_hie's GlowUp Salon.
  </div>
</div>"""


def send_booking_confirmation(appointment):
    """Confirm a new booking to the client and notify the assigned stylist."""
    when    = _format_when(appointment)
    service = appointment.service.name
    stylist = str(appointment.staff)
    client  = appointment.client

    # ── Client confirmation ──
    client_lines = [
        f"Hi {client.first_name or client.username},",
        "Your appointment is booked! 🎉",
        f"<strong>Service:</strong> {service}",
        f"<strong>Stylist:</strong> {stylist}",
        f"<strong>When:</strong> {when}",
        "We can't wait to see you. To change or cancel, visit "
        "“My Appointments” on the site.",
    ]
    _send(
        subject=f"Your {service} appointment is confirmed",
        to_email=client.email,
        text_body=(
            f"Hi {client.first_name or client.username},\n\n"
            f"Your appointment is booked!\n\n"
            f"Service: {service}\nStylist: {stylist}\nWhen: {when}\n\n"
            "See you soon!\nFav_hie's GlowUp Salon"
        ),
        html_body=_wrap_html('Appointment Confirmed', client_lines),
    )

    # ── Stylist notification ──
    staff_email = appointment.staff.user.email
    staff_lines = [
        f"Hi {appointment.staff.user.first_name or 'there'},",
        "You have a new booking:",
        f"<strong>Client:</strong> {client.get_full_name() or client.username}",
        f"<strong>Service:</strong> {service}",
        f"<strong>When:</strong> {when}",
    ]
    if appointment.notes:
        staff_lines.append(f"<strong>Notes:</strong> {appointment.notes}")
    _send(
        subject=f"New booking: {service} — {when}",
        to_email=staff_email,
        text_body=(
            f"New booking.\n\nClient: {client.get_full_name() or client.username}\n"
            f"Service: {service}\nWhen: {when}\n"
            + (f"Notes: {appointment.notes}\n" if appointment.notes else "")
        ),
        html_body=_wrap_html('New Booking', staff_lines),
    )


def send_cancellation_notice(appointment):
    """Tell the client and stylist that an appointment was cancelled."""
    when    = _format_when(appointment)
    service = appointment.service.name
    client  = appointment.client

    client_lines = [
        f"Hi {client.first_name or client.username},",
        "Your appointment has been cancelled:",
        f"<strong>Service:</strong> {service}",
        f"<strong>When:</strong> {when}",
        "Changed your mind? You can book again any time on the site.",
    ]
    _send(
        subject=f"Your {service} appointment was cancelled",
        to_email=client.email,
        text_body=(
            f"Hi {client.first_name or client.username},\n\n"
            f"Your appointment has been cancelled.\n\n"
            f"Service: {service}\nWhen: {when}\n\n"
            "Book again any time!\nFav_hie's GlowUp Salon"
        ),
        html_body=_wrap_html('Appointment Cancelled', client_lines),
    )

    staff_email = appointment.staff.user.email
    staff_lines = [
        "A booking was cancelled:",
        f"<strong>Client:</strong> {client.get_full_name() or client.username}",
        f"<strong>Service:</strong> {service}",
        f"<strong>When:</strong> {when}",
    ]
    _send(
        subject=f"Cancelled: {service} — {when}",
        to_email=staff_email,
        text_body=(
            f"A booking was cancelled.\n\n"
            f"Client: {client.get_full_name() or client.username}\n"
            f"Service: {service}\nWhen: {when}\n"
        ),
        html_body=_wrap_html('Booking Cancelled', staff_lines),
    )
