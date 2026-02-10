from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time
from bookings.models import Show, Spot, Coupon


class Command(BaseCommand):
    help = "Create sample shows, spots, and a coupon for testing."

    def handle(self, *args, **options):
        days = ["Tue", "Wed", "Thu", "Fri"]
        for i in range(4):
            d = timezone.localdate() + timedelta(days=i)
            show, created = Show.objects.get_or_create(
                date=d,
                defaults={"label": f"{days[i % 4]}, {d.day} {d.strftime('%B')}"},
            )
            if created:
                self.stdout.write(f"Created show: {show.label}")
            for slot in [
                (time(14, 20), 15, 150, ""),
                (time(16, 0), 12, 150, ""),
                (time(17, 30), 8, 150, ""),
                (time(19, 0), 6, 150, ""),
                (time(20, 30), 6, 150, "Competitive Mic" if i == 0 else ""),
                (time(22, 0), 10, 150, ""),
            ]:
                t, dur, price, stype = slot
                Spot.objects.get_or_create(
                    show=show,
                    time=t,
                    defaults={
                        "duration_minutes": dur,
                        "price": price,
                        "spot_type": stype,
                        "max_slots": 1,
                    },
                )
        Coupon.objects.get_or_create(
            code="iLoveVC2",
            defaults={
                "description": "Book 6+ spots at ₹100/spot",
                "min_spots": 6,
                "discount_type": "fixed",
                "discount_value": 100,
                "is_active": True,
            },
        )
        self.stdout.write(self.style.SUCCESS("Seed complete: shows, spots, and coupon iLoveVC2."))
