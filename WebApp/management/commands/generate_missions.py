from django.core.management.base import BaseCommand
from ...models import Mission  # Ensure correct app name

class Command(BaseCommand):
    help = "Generates daily missions"

    def handle(self, *args, **kwargs):
        missions = [
            {"name": "Recycle!", "description": "Use one of the many recycling bins on our campus.", "requires_location": False, "latitude": None, "longitude": None, "points": 10},
            {"name": "Visit the Forum Library!", "description": "Verify your location!", "latitude": 50.735932, "longitude": -3.534415, "requires_location": True, "points": 50}
        ]

        for mission_data in missions:
            Mission.objects.update_or_create(
                name=mission_data["name"],
                defaults=mission_data
            )

        self.stdout.write(self.style.SUCCESS("✅ Daily missions generated successfully!"))
