from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.bot.utils import send_telegram_notification
from apps.membership.models import Membership
from apps.payments.models import Payment


@shared_task
def mark_expired_memberships():
    today = timezone.now().date()
    expired_memberships = Membership.objects.filter(
        end_date__lt=today,
        status__in=[Membership.Status.ACTIVE, Membership.Status.FROZEN]
    )

    for membership in expired_memberships:
        membership.status = Membership.Status.EXPIRED
        membership.save()

        message = (
            f"Membership Expired\n"
            f"Member: {membership.member.get_full_name()}\n"
            f"Email: {membership.member.email}\n"
            f"Plan: {membership.plan.name}\n"
            f"End Date: {membership.end_date}"
        )
        send_telegram_notification(message)

    return f"Markedmemberships as expired"


@shared_task
def send_expiration_reminders(days_before=7):
    target_date = timezone.now().date() + timedelta(days=days_before)

    memberships = Membership.objects.filter(
        end_date=target_date,
        status=Membership.Status.ACTIVE
    )

    count = 0
    for membership in memberships:
        message = (
            f"⏰ Membership Expiring Soon\n"
            f"Member: {membership.member.get_full_name()}\n"
            f"Email: {membership.member.email}\n"
            f"Plan: {membership.plan.name}\n"
            f"Expires in: {days_before} day(s)\n"
            f"End Date: {membership.end_date}"
        )
        send_telegram_notification(message)
        count += 1

    return f"Sent {count} expiration reminders for {days_before} days before"


@shared_task
def auto_renew_memberships():
    today = timezone.now().date()

    expired_auto_renew = Membership.objects.filter(
        auto_renew=True,
        status=Membership.Status.EXPIRED,
        end_date__lt=today
    )

    count = 0
    for old_membership in expired_auto_renew:
        has_pending = Payment.objects.filter(
            user=old_membership.member,
            status=Payment.StatusChoices.PENDING
        ).exists()

        if has_pending:
            continue

        new_membership = Membership.objects.create(
            member=old_membership.member,
            plan=old_membership.plan,
            start_date=today,
            end_date=today + timedelta(days=old_membership.plan.duration_days),
            status=Membership.Status.ACTIVE,
            auto_renew=True,
            price_at_purchase=old_membership.plan.price
        )

        old_membership.auto_renew = False
        old_membership.save()

        message = (
            f"Auto-Renewal Successful\n"
            f"Member: {new_membership.member.get_full_name()}\n"
            f"Email: {new_membership.member.email}\n"
            f"Plan: {new_membership.plan.name}\n"
            f"New Start Date: {new_membership.start_date}\n"
            f"New End Date: {new_membership.end_date}"
        )
        send_telegram_notification(message)
        count += 1

    return f"Auto-renewed {count} memberships"


@shared_task
def notify_new_membership(membership_id):
    try:
        membership = Membership.objects.get(id=membership_id)
        message = (
            f"New Membership Created\n"
            f"Member: {membership.member.get_full_name()}\n"
            f"Email: {membership.member.email}\n"
            f"Plan: {membership.plan.name} ({membership.plan.tier})\n"
            f"Price: ${membership.price_at_purchase}\n"
            f"Start Date: {membership.start_date}\n"
            f"End Date: {membership.end_date}\n"
            f"Auto-Renew: {'Yes' if membership.auto_renew else 'No'}"
        )
        send_telegram_notification(message)

        return f"Notification sent for membership {membership_id}"

    except Membership.DoesNotExist:
        return f"Membership {membership_id} not found"


@shared_task
def notify_membership_frozen(membership_id):
    try:
        membership = Membership.objects.get(id=membership_id)
        message = (
            f"❄️ Membership Frozen\n"
            f"Member: {membership.member.get_full_name()}\n"
            f"Email: {membership.member.email}\n"
            f"Plan: {membership.plan.name}\n"
            f"Frozen From: {membership.frozen_from}\n"
            f"Frozen To: {membership.frozen_to}\n"
            f"New End Date: {membership.end_date}"
        )
        send_telegram_notification(message)

        return f"Freeze notification sent for membership {membership_id}"

    except Membership.DoesNotExist:
        return f"Membership {membership_id} not found"


@shared_task
def notify_payment_success(payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)

        membership = Membership.objects.get(id=payment.membership_id)

        message = (
            f"Payment Successful\n"
            f"Payment ID: {payment.id}\n"
            f"Type: {payment.get_type_display()}\n"
            f"Amount: ${payment.money_to_pay}\n"
            f"Member: {membership.member.get_full_name()}\n"
            f"Email: {membership.member.email}\n"
            f"Plan: {membership.plan.name}\n"
            f"Session ID: {payment.session_id}"
        )
        send_telegram_notification(message)

        return f"Payment success notification sent for payment {payment_id}"

    except Payment.DoesNotExist:
        return f"Payment {payment_id} not found"

    except Membership.DoesNotExist:
        return f"Membership for payment {payment_id} not found"
