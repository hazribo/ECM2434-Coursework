from django.core.management.base import BaseCommand
from ...models import Mission

class Command(BaseCommand):
    help = 'Generates daily missions'

    def handle(self, *args, **kwargs):
        missions = [
            {"name": "Recycle!", "description": "Use one of the many recycling bins on our campus."},
            {"name": "Visit [Location]!", "description": "Scan the QR Code at [Location]."},
            {"name": "Visit [Location]!", "description": "Scan the QR Code at [Location]."},
        ]

        for mission_data in missions:
            Mission.objects.get_or_create(**mission_data)

        self.stdout.write(self.style.SUCCESS('Daily missions generated successfully!'))