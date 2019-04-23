from django.core.management.base import BaseCommand
from django.utils import timezone

from django_ticketoffice.models import Ticket


class Command(BaseCommand):

    help = """Clean out expired tickets."""

    def handle(self, *args, **options):
        Ticket.objects.filter(expiry_datetime__lt=timezone.now()).delete()
