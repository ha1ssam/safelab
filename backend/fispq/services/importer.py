"""
FISPQ Importer Service.

Orchestrates the process of fetching data from PubChem and populating
both the Substance and FISPQ models. Designed to be called from
management commands or admin actions.

Flow:
  1. Search PubChem for the compound (by CAS or name)
  2. Fetch full data (properties, GHS, physical)
  3. Create/update the Substance record
  4. Create/update the FISPQ record
  5. Map GHS → hazard codes and attach to substance
"""

import logging
from decimal import Decimal, InvalidOperation
from typing import Optional

from django.db import transaction

from hazards.models import Hazard
from substances.models import Substance
from fispq.models import FISPQ

from .pubchem_client import PubChemClient, PubChemError
from .ghs_mapping import map_ghs_to_hazard_codes, infer_reactivity_flags

logger = logging.getLogger(__name__)


def _make_json_safe(obj):
    """Recursively convert Decimal values to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_make_json_safe(i) for i in obj]
    return obj


class ImportResult:
    """Tracks the outcome of an import operation."""

    def __init__(self):
        self.created: list[str] = []
        self.updated: list[str] = []
        self.skipped: list[str] = []
        self.errors: list[tuple[str, str]] = []

    @property
    def total(self) -> int:
        return len(self.created) + len(self.updated) + len(self.skipped) + len(self.errors)

    def summary(self) -> str:
        return (
            f"Criados: {len(self.created)} | "
            f"Atualizados: {len(self.updated)} | "
            f"Ignorados: {len(self.skipped)} | "
            f"Erros: {len(self.errors)}"
        )


class SubstanceImporter:
    """Imports substances from PubChem into the local database."""

    def __init__(self):
        self.client = PubChemClient()
        self._hazards_cache: dict[str, Hazard] = {}

    def _get_hazard(self, code: str) -> Optional[Hazard]:
        if code not in self._hazards_cache:
            try:
                self._hazards_cache[code] = Hazard.objects.get(code=code)
            except Hazard.DoesNotExist:
                logger.warning(f"Hazard code '{code}' not found in DB")
                return None
        return self._hazards_cache[code]

    @transaction.atomic
    def import_by_cas(self, cas_number: str, name_hint: str = "") -> Optional[Substance]:
        """
        Import a single substance by CAS number.
        Returns the Substance instance or None on failure.
        """
        cid = self.client.search_by_cas(cas_number)
        if not cid:
            logger.error(f"CAS {cas_number} not found on PubChem")
            return None

        substance, _ = self._import_compound(cid, cas_number=cas_number, name_hint=name_hint)
        return substance

    @transaction.atomic
    def import_by_name(self, name: str) -> Optional[Substance]:
        """
        Import a single substance by name.
        Returns the Substance instance or None on failure.
        """
        cid = self.client.search_by_name(name)
        if not cid:
            logger.error(f"'{name}' not found on PubChem")
            return None

        substance, _ = self._import_compound(cid, name_hint=name)
        return substance

    @transaction.atomic
    def import_by_cid(self, cid: int, name_hint: str = "") -> Optional[Substance]:
        """Import a single substance by PubChem CID."""
        substance, _ = self._import_compound(cid, name_hint=name_hint)
        return substance

    def _import_compound(
        self, cid: int, cas_number: str = "", name_hint: str = ""
    ) -> tuple[Optional[Substance], bool]:
        """Core import logic. Returns (substance, created)."""
        try:
            data = self.client.get_full_compound_data(cid)
        except PubChemError as e:
            logger.error(f"Failed to fetch CID {cid}: {e}")
            return None, False

        basic = data.get("basic", {})
        ghs = data.get("ghs", {})
        physical = data.get("physical", {})

        # Determine name
        name = name_hint or basic.get("IUPACName", f"CID-{cid}")
        formula = basic.get("MolecularFormula", "")
        molar_mass = self._fit_decimal(
            self._to_decimal(basic.get("MolecularWeight")),
            max_digits=8, decimal_places=3,
        )

        # Determine CAS (might already be known)
        if not cas_number:
            cas_number = ""

        # Infer reactivity flags
        substance_data = {
            "cas_number": cas_number,
            "formula": formula,
            "name": name,
            "ph_value": physical.get("ph_value"),
        }
        reactivity_flags = infer_reactivity_flags(ghs, substance_data)

        # Build PPE list from FISPQ data
        ppe_list = ghs.get("recommended_ppe", [])
        if not ppe_list:
            ppe_list = self._default_ppe_from_ghs(ghs)

        # Create/update Substance
        defaults = {
            "name": name,
            "formula": formula,
            "cas_number": cas_number,
            "physical_state": self._infer_physical_state(physical, formula),
            "molar_mass": molar_mass,
            "is_acid": reactivity_flags["is_acid"],
            "is_base": reactivity_flags["is_base"],
            "is_water": reactivity_flags["is_water"],
            "is_organic_solvent": reactivity_flags["is_organic_solvent"],
            "required_ppe": ppe_list,
        }

        if cas_number:
            # Try to find by CAS first, then by name as fallback
            existing = Substance.objects.filter(cas_number=cas_number).first()
            if not existing:
                existing = Substance.objects.filter(name=name).first()
            if existing:
                for k, v in defaults.items():
                    setattr(existing, k, v)
                existing.save()
                substance, created = existing, False
            else:
                substance = Substance.objects.create(**defaults)
                created = True
        else:
            substance, created = Substance.objects.update_or_create(
                name=name,
                defaults=defaults,
            )

        # Map GHS to hazard codes and attach
        hazard_codes = map_ghs_to_hazard_codes(ghs)
        hazards = [self._get_hazard(c) for c in hazard_codes]
        hazards = [h for h in hazards if h is not None]
        if hazards:
            substance.hazards.set(hazards)

        # Create/update FISPQ record
        fispq_defaults = {
            "data_source": FISPQ.DataSource.PUBCHEM,
            "source_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}",
            "pubchem_cid": cid,
            "ghs_classification": ghs.get("ghs_classification", []),
            "signal_word": ghs.get("signal_word", ""),
            "h_phrases": self._format_h_phrases(ghs.get("h_phrases", [])),
            "p_phrases": self._format_p_phrases(ghs.get("p_phrases", [])),
            "ghs_pictograms": ghs.get("pictograms", []),
            "incompatible_chemicals": physical.get("incompatible_materials", []),
            "raw_data": _make_json_safe(data),
            "is_complete": bool(ghs.get("ghs_classification")),
        }

        # Physical properties — coerce to fit DecimalField bounds. Out-of-range
        # values are dropped (None) rather than crashing on insert/read.
        decimal_fields = {
            "boiling_point":   (7, 2),
            "melting_point":   (7, 2),
            "density":         (7, 4),
            "flash_point":     (7, 2),
            "vapor_pressure":  (10, 3),
            "log_p":           (6, 3),
        }
        for field, (md, dp) in decimal_fields.items():
            raw = physical.get(field)
            if isinstance(raw, Decimal):
                fitted = self._fit_decimal(raw, md, dp)
                if fitted is not None:
                    fispq_defaults[field] = fitted
        if isinstance(physical.get("solubility_water"), str):
            fispq_defaults["solubility_water"] = physical["solubility_water"][:120]

        # Avoid UNIQUE constraint on pubchem_cid: another FISPQ may already
        # reference this CID (multiple lab_catalog entries can resolve to the
        # same PubChem compound). Detach the CID from the previous record
        # before assigning it to the new one. Use values_list to avoid
        # triggering the Decimal converter on potentially corrupted rows.
        cid_owner = (
            FISPQ.objects.filter(pubchem_cid=cid)
            .exclude(substance=substance)
            .values_list("pk", flat=True)
            .first()
        )
        if cid_owner is not None:
            FISPQ.objects.filter(pk=cid_owner).update(pubchem_cid=None)

        # Avoid update_or_create: it issues a SELECT that goes through Django's
        # converters, which can crash on legacy rows with Decimal values that
        # exceed the field's max_digits. Use a PK-only existence check + update.
        existing_pk = (
            FISPQ.objects.filter(substance=substance)
            .values_list("pk", flat=True)
            .first()
        )
        if existing_pk is not None:
            FISPQ.objects.filter(pk=existing_pk).update(**fispq_defaults)
        else:
            FISPQ.objects.create(substance=substance, **fispq_defaults)

        action = "created" if created else "updated"
        logger.info(f"[{action}] {substance.name} (CID: {cid})")
        return substance, created

    def bulk_import(self, compounds: list[dict]) -> ImportResult:
        """
        Import a batch of compounds.
        Each item: {"cas": "...", "name": "..."} — at least one required.
        """
        result = ImportResult()

        for item in compounds:
            cas = item.get("cas", "")
            name = item.get("name", "")
            identifier = cas or name

            try:
                with transaction.atomic():
                    if cas:
                        cid = self.client.search_by_cas(cas)
                    else:
                        cid = self.client.search_by_name(name)

                    if not cid:
                        result.skipped.append(identifier)
                        continue

                    substance, created = self._import_compound(
                        cid, cas_number=cas, name_hint=name
                    )

                if substance is None:
                    result.skipped.append(identifier)
                elif created:
                    result.created.append(identifier)
                else:
                    result.updated.append(identifier)
            except Exception as e:
                logger.exception(f"Error importing {identifier}")
                result.errors.append((identifier, str(e)))

        return result

    # ─── Helpers ─────────────────────────────────────────────────────────

    def _to_decimal(self, value) -> Optional[Decimal]:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None

    def _fit_decimal(
        self,
        value: Optional[Decimal],
        max_digits: int,
        decimal_places: int,
    ) -> Optional[Decimal]:
        """
        Quantize and bounds-check a Decimal so it fits a Django DecimalField.
        Returns None if the value cannot be represented (so the field stays NULL
        instead of triggering a sqlite quantize error on read).
        """
        if value is None:
            return None
        try:
            quant = Decimal(10) ** -decimal_places
            quantized = value.quantize(quant)
        except InvalidOperation:
            return None

        max_int_digits = max_digits - decimal_places
        limit = Decimal(10) ** max_int_digits
        if quantized.copy_abs() >= limit:
            return None
        return quantized

    def _infer_physical_state(self, physical: dict, formula: str) -> str:
        bp = physical.get("boiling_point")
        mp = physical.get("melting_point")

        if isinstance(bp, Decimal) and bp < Decimal("25"):
            return "gas"
        if isinstance(mp, Decimal) and mp > Decimal("25"):
            return "solid"
        return "liquid"

    def _default_ppe_from_ghs(self, ghs: dict) -> list[str]:
        """Infer basic PPE from GHS pictograms."""
        ppe = ["óculos de proteção"]
        pictograms = ghs.get("pictograms", [])

        if "GHS05" in pictograms or "GHS06" in pictograms:
            ppe.extend(["luvas nitrílicas", "jaleco", "face shield"])
        elif "GHS07" in pictograms:
            ppe.extend(["luvas nitrílicas", "jaleco"])
        else:
            ppe.append("luvas")

        if "GHS02" in pictograms:
            ppe.append("manter longe de fontes de ignição")

        return ppe

    def _format_h_phrases(self, phrases: list) -> list[dict]:
        """Normalize H-phrases to [{code, text}] format."""
        import re
        result = []
        for p in phrases:
            text = p if isinstance(p, str) else str(p)
            match = re.match(r"(H\d{3})\s*[:\-]?\s*(.*)", text)
            if match:
                result.append({"code": match.group(1), "text": match.group(2).strip()})
            else:
                result.append({"code": "", "text": text})
        return result

    def _format_p_phrases(self, phrases: list) -> list[dict]:
        """Normalize P-phrases to [{code, text}] format."""
        import re
        result = []
        for p in phrases:
            text = p if isinstance(p, str) else str(p)
            match = re.match(r"(P\d{3}(?:\+P\d{3})*)\s*[:\-]?\s*(.*)", text)
            if match:
                result.append({"code": match.group(1), "text": match.group(2).strip()})
            else:
                result.append({"code": "", "text": text})
        return result
