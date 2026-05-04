"""
PubChem PUG REST API client.

Fetches chemical compound data including GHS classification, physical
properties, and safety information. Rate-limited to respect PubChem's
5 requests/second policy.

API docs: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
"""

import logging
import time
from decimal import Decimal, InvalidOperation
from typing import Optional

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
VIEW_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view"

REQUEST_DELAY = 0.25  # 4 req/s to stay safely under 5/s limit
REQUEST_TIMEOUT = 30


class PubChemError(Exception):
    pass


class PubChemClient:
    """Stateless client for PubChem PUG REST."""

    def __init__(self):
        self._last_request_time = 0.0
        self._session = requests.Session()
        self._session.headers.update({
            "Accept": "application/json",
            "User-Agent": "BioSafeLab/1.0 (academic research; chemical safety)",
        })

    def _throttle(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self._last_request_time = time.time()

    def _get(self, url: str) -> dict:
        self._throttle()
        try:
            resp = self._session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                raise PubChemError(f"Compound not found: {url}")
            raise PubChemError(f"PubChem API error: {e}")
        except requests.exceptions.RequestException as e:
            raise PubChemError(f"Network error: {e}")

    # ─── Search ──────────────────────────────────────────────────────────

    def search_by_name(self, name: str) -> Optional[int]:
        """Search for a compound by name, return CID or None."""
        url = f"{BASE_URL}/compound/name/{requests.utils.quote(name)}/cids/JSON"
        try:
            data = self._get(url)
            cids = data.get("IdentifierList", {}).get("CID", [])
            return cids[0] if cids else None
        except PubChemError:
            return None

    def search_by_cas(self, cas_number: str) -> Optional[int]:
        """Search for a compound by CAS registry number, return CID or None."""
        url = f"{BASE_URL}/compound/name/{requests.utils.quote(cas_number)}/cids/JSON"
        try:
            data = self._get(url)
            cids = data.get("IdentifierList", {}).get("CID", [])
            return cids[0] if cids else None
        except PubChemError:
            return None

    # ─── Compound properties ─────────────────────────────────────────────

    def get_properties(self, cid: int) -> dict:
        """Fetch basic properties for a compound by CID."""
        props = (
            "MolecularFormula,MolecularWeight,IUPACName,"
            "ExactMass,CanonicalSMILES,IsomericSMILES,InChI"
        )
        url = f"{BASE_URL}/compound/cid/{cid}/property/{props}/JSON"
        data = self._get(url)
        properties = data.get("PropertyTable", {}).get("Properties", [])
        return properties[0] if properties else {}

    # ─── GHS Classification (PUG View) ───────────────────────────────────

    def get_ghs_data(self, cid: int) -> dict:
        """
        Fetch GHS safety data from PubChem's PUG View API.
        Returns structured dict with classification, H/P phrases, pictograms.
        """
        url = (
            f"{VIEW_URL}/data/compound/{cid}/JSON"
            f"?heading=GHS+Classification"
        )
        try:
            data = self._get(url)
        except PubChemError:
            logger.warning(f"No GHS data for CID {cid}")
            return {}

        return self._parse_ghs_response(data)

    def _parse_ghs_response(self, data: dict) -> dict:
        """Extract GHS info from the nested PUG View JSON structure."""
        import re

        result = {
            "pictograms": [],
            "signal_word": "",
            "h_phrases": [],
            "p_phrases": [],
            "ghs_classification": [],
        }

        try:
            record = data["Record"]
            sections = record.get("Section", [])
        except (KeyError, TypeError):
            return result

        # First, try structured extraction via section headings
        for section in sections:
            self._walk_ghs_section(section, result)

        # If structured parsing didn't find H-phrases, parse from classification strings
        # PubChem often returns all GHS info as flat strings in the classification list
        if not result["h_phrases"] and result["ghs_classification"]:
            parsed_h = []
            parsed_p = []
            parsed_classes = []
            for entry in result["ghs_classification"]:
                if entry in ("Danger", "Warning"):
                    result["signal_word"] = entry
                elif re.match(r"H\d{3}", entry):
                    parsed_h.append(entry)
                elif re.search(r":\s*H\d{3}", entry):
                    parsed_h.append(entry)
                elif re.match(r"P\d{3}", entry):
                    parsed_p.append(entry)
                else:
                    parsed_classes.append(entry)

            if parsed_h:
                result["h_phrases"] = parsed_h
            if parsed_p:
                result["p_phrases"] = parsed_p
            if parsed_classes:
                result["ghs_classification"] = parsed_classes
            elif parsed_h or parsed_p:
                result["ghs_classification"] = []

        return result

    def _walk_ghs_section(self, section: dict, result: dict):
        """Recursively walk PUG View sections extracting GHS data."""
        heading = section.get("TOCHeading", "")

        if heading == "GHS Hazard Statements":
            result["h_phrases"] = self._extract_string_values(section)
        elif heading == "Precautionary Statement Codes":
            result["p_phrases"] = self._extract_string_values(section)
        elif heading == "GHS Classification":
            result["ghs_classification"] = self._extract_string_values(section)
        elif heading == "Pictogram(s)":
            result["pictograms"] = self._extract_pictogram_codes(section)
        elif heading == "Signal":
            values = self._extract_string_values(section)
            if values:
                result["signal_word"] = values[0]

        for subsection in section.get("Section", []):
            self._walk_ghs_section(subsection, result)

    def _extract_string_values(self, section: dict) -> list[str]:
        """Extract StringWithMarkup values from a section's Information."""
        values = []
        for info in section.get("Information", []):
            for val in info.get("Value", {}).get("StringWithMarkup", []):
                text = val.get("String", "").strip()
                if text:
                    values.append(text)
        return values

    def _extract_pictogram_codes(self, section: dict) -> list[str]:
        """Extract GHS pictogram codes (GHS01-GHS09) from markup."""
        codes = []
        for info in section.get("Information", []):
            for val in info.get("Value", {}).get("StringWithMarkup", []):
                for markup in val.get("Markup", []):
                    extra = markup.get("Extra", "")
                    if extra.startswith("GHS"):
                        codes.append(extra)
        return codes

    # ─── Physical properties (PUG View) ──────────────────────────────────

    def get_physical_properties(self, cid: int) -> dict:
        """Fetch physical/chemical properties from PUG View."""
        url = (
            f"{VIEW_URL}/data/compound/{cid}/JSON"
            f"?heading=Experimental+Properties"
        )
        try:
            data = self._get(url)
        except PubChemError:
            return {}

        return self._parse_physical_properties(data)

    def _parse_physical_properties(self, data: dict) -> dict:
        """Extract boiling point, melting point, density, flash point etc."""
        result = {}
        try:
            record = data["Record"]
            sections = record.get("Section", [])
        except (KeyError, TypeError):
            return result

        for section in sections:
            self._walk_physical_section(section, result)

        return result

    def _walk_physical_section(self, section: dict, result: dict):
        heading = section.get("TOCHeading", "")

        property_map = {
            "Boiling Point": "boiling_point",
            "Melting Point": "melting_point",
            "Density": "density",
            "Flash Point": "flash_point",
            "Vapor Pressure": "vapor_pressure",
            "Solubility": "solubility_water",
            "LogP": "log_p",
            "Auto-Ignition": "auto_ignition_temp",
        }

        for keyword, field_name in property_map.items():
            if keyword in heading:
                values = self._extract_string_values(section)
                if values:
                    result[field_name] = self._try_parse_numeric(values[0])
                break

        for subsection in section.get("Section", []):
            self._walk_physical_section(subsection, result)

    def _try_parse_numeric(self, value: str) -> str | Decimal:
        """Try to extract a numeric value from a property string."""
        import re
        match = re.search(r"[-+]?\d*\.?\d+", value)
        if match:
            try:
                return Decimal(match.group())
            except InvalidOperation:
                pass
        return value

    # ─── Full compound fetch ─────────────────────────────────────────────

    def get_full_compound_data(self, cid: int) -> dict:
        """
        Fetch all relevant data for a compound — properties, GHS, physical.
        Returns a consolidated dictionary.
        """
        basic = self.get_properties(cid)
        ghs = self.get_ghs_data(cid)
        physical = self.get_physical_properties(cid)

        return {
            "cid": cid,
            "basic": basic,
            "ghs": ghs,
            "physical": physical,
        }
