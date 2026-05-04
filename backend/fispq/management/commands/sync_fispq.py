"""
Management command: sync Substance flags/hazards from FISPQ data.

Ensures consistency between FISPQ records (source of truth for external
data) and the Substance model flags used by the rules engine.

Usage:
    python manage.py sync_fispq          # sync all
    python manage.py sync_fispq --id 5   # sync a single substance
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from hazards.models import Hazard
from substances.models import Substance
from fispq.models import FISPQ
from fispq.services.ghs_mapping import map_ghs_to_hazard_codes, infer_reactivity_flags


class Command(BaseCommand):
    help = "Sincroniza flags e riscos das substâncias a partir dos dados FISPQ."

    def add_arguments(self, parser):
        parser.add_argument(
            "--id",
            type=int,
            help="Sincronizar apenas a substância com este ID.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Mostra alterações sem aplicá-las.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        queryset = FISPQ.objects.select_related("substance").prefetch_related(
            "substance__hazards"
        )

        if options["id"]:
            queryset = queryset.filter(substance_id=options["id"])

        if not queryset.exists():
            self.stdout.write(self.style.WARNING("Nenhuma FISPQ encontrada."))
            return

        hazards_by_code = {h.code: h for h in Hazard.objects.all()}
        updated = 0

        for fispq in queryset:
            substance = fispq.substance
            changes = []

            # Sync hazard codes from GHS data
            ghs_data = {
                "ghs_classification": fispq.ghs_classification or [],
                "h_phrases": fispq.h_phrases or [],
                "pictograms": fispq.ghs_pictograms or [],
            }
            new_hazard_codes = map_ghs_to_hazard_codes(ghs_data)
            current_codes = set(substance.hazards.values_list("code", flat=True))

            if new_hazard_codes != current_codes:
                changes.append(f"hazards: {current_codes} → {new_hazard_codes}")
                if not options["dry_run"]:
                    hazards = [
                        hazards_by_code[c] for c in new_hazard_codes
                        if c in hazards_by_code
                    ]
                    substance.hazards.set(hazards)

            # Sync reactivity flags
            substance_data = {
                "cas_number": substance.cas_number,
                "formula": substance.formula,
                "ph_value": substance.ph_value,
            }
            flags = infer_reactivity_flags(ghs_data, substance_data)

            for flag_name, flag_value in flags.items():
                current = getattr(substance, flag_name)
                if current != flag_value:
                    changes.append(f"{flag_name}: {current} → {flag_value}")
                    if not options["dry_run"]:
                        setattr(substance, flag_name, flag_value)

            if changes:
                if not options["dry_run"]:
                    substance.save()
                updated += 1
                prefix = "[dry-run] " if options["dry_run"] else ""
                self.stdout.write(f"  {prefix}{substance.name}: {', '.join(changes)}")

        self.stdout.write(
            self.style.SUCCESS(f"\n{updated} substância(s) {'seriam ' if options['dry_run'] else ''}atualizadas.")
        )
