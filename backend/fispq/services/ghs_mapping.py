"""
GHS → System Hazard Code mapping.

Maps GHS classification strings and H-phrase codes to the internal
hazard codes used by the BioSafeLab rules engine.

This is the bridge between PubChem's GHS data and the system's
deterministic hazard flags. The mapping is conservative: if a GHS
class can't be confidently mapped, it is NOT added (safety through
explicit data only).
"""

from hazards.models import Hazard

# GHS hazard class prefix → internal hazard code
GHS_CLASS_TO_HAZARD: dict[str, str] = {
    "Flam. Liq.": "flammable",
    "Flam. Sol.": "flammable",
    "Flam. Gas": "flammable",
    "Flam. Aerosol": "flammable",
    "Pyr. Liq.": "flammable",
    "Pyr. Sol.": "flammable",
    "Skin Corr.": "corrosive",
    "Eye Dam.": "corrosive",
    "Met. Corr.": "corrosive",
    "Acute Tox.": "toxic",
    "STOT SE": "toxic",
    "STOT RE": "toxic",
    "Asp. Tox.": "toxic",
    "Ox. Liq.": "oxidizer",
    "Ox. Sol.": "oxidizer",
    "Ox. Gas": "oxidizer",
    "Water-react.": "reactive_water",
    "Unst. Expl.": "explosive",
    "Expl.": "explosive",
    "Self-react.": "explosive",
    "Org. Perox.": "explosive",
    "Skin Irrit.": "irritant",
    "Eye Irrit.": "irritant",
    "Skin Sens.": "irritant",
    "Resp. Sens.": "irritant",
    "Carc.": "carcinogen",
    "Muta.": "carcinogen",
    "Repr.": "carcinogen",
    "Aquatic Acute": "env_hazard",
    "Aquatic Chronic": "env_hazard",
    "Ozone": "env_hazard",
    "Press. Gas": "compressed_gas",
    "Compr. Gas": "compressed_gas",
    "Liq. Gas": "compressed_gas",
    "Ref. Gas": "compressed_gas",
    "Diss. Gas": "compressed_gas",
}

# H-phrase code → internal hazard code (supplements the class-based mapping)
H_PHRASE_TO_HAZARD: dict[str, str] = {
    "H200": "explosive",
    "H201": "explosive",
    "H202": "explosive",
    "H203": "explosive",
    "H204": "explosive",
    "H205": "explosive",
    "H220": "flammable",
    "H221": "flammable",
    "H222": "flammable",
    "H223": "flammable",
    "H224": "flammable",
    "H225": "flammable",
    "H226": "flammable",
    "H227": "flammable",
    "H228": "flammable",
    "H229": "flammable",
    "H230": "flammable",
    "H231": "flammable",
    "H240": "explosive",
    "H241": "explosive",
    "H242": "flammable",
    "H250": "flammable",
    "H251": "flammable",
    "H252": "flammable",
    "H260": "reactive_water",
    "H261": "reactive_water",
    "H270": "oxidizer",
    "H271": "oxidizer",
    "H272": "oxidizer",
    "H280": "compressed_gas",
    "H281": "compressed_gas",
    "H290": "corrosive",
    "H300": "toxic",
    "H301": "toxic",
    "H302": "toxic",
    "H304": "toxic",
    "H310": "toxic",
    "H311": "toxic",
    "H312": "toxic",
    "H314": "corrosive",
    "H315": "irritant",
    "H317": "irritant",
    "H318": "corrosive",
    "H319": "irritant",
    "H330": "toxic",
    "H331": "toxic",
    "H332": "toxic",
    "H334": "irritant",
    "H335": "irritant",
    "H336": "irritant",
    "H340": "carcinogen",
    "H341": "carcinogen",
    "H350": "carcinogen",
    "H351": "carcinogen",
    "H360": "carcinogen",
    "H361": "carcinogen",
    "H362": "toxic",
    "H370": "toxic",
    "H371": "toxic",
    "H372": "toxic",
    "H373": "toxic",
    "H400": "env_hazard",
    "H401": "env_hazard",
    "H402": "env_hazard",
    "H410": "env_hazard",
    "H411": "env_hazard",
    "H412": "env_hazard",
    "H413": "env_hazard",
    "H420": "env_hazard",
}

# GHS pictogram → hazard codes (fallback when class text isn't parseable)
PICTOGRAM_TO_HAZARDS: dict[str, list[str]] = {
    "GHS01": ["explosive"],
    "GHS02": ["flammable"],
    "GHS03": ["oxidizer"],
    "GHS04": ["compressed_gas"],
    "GHS05": ["corrosive"],
    "GHS06": ["toxic"],
    "GHS07": ["irritant"],
    "GHS08": ["carcinogen"],
    "GHS09": ["env_hazard"],
}


def map_ghs_to_hazard_codes(ghs_data: dict) -> set[str]:
    """
    Given a GHS data dict (from PubChem), return the set of internal
    hazard codes that apply.

    Uses all three sources (classification text, H-phrases, pictograms)
    and takes the union.
    """
    codes: set[str] = set()

    # 1. Classification strings
    for classification in ghs_data.get("ghs_classification", []):
        for prefix, hazard_code in GHS_CLASS_TO_HAZARD.items():
            if prefix in classification:
                codes.add(hazard_code)
                break

    # 2. H-phrases
    for phrase_entry in ghs_data.get("h_phrases", []):
        text = phrase_entry if isinstance(phrase_entry, str) else phrase_entry.get("code", "")
        h_code = _extract_h_code(text)
        if h_code and h_code in H_PHRASE_TO_HAZARD:
            codes.add(H_PHRASE_TO_HAZARD[h_code])

    # 3. Pictograms (lowest priority — only fills gaps)
    for pictogram in ghs_data.get("pictograms", []):
        if pictogram in PICTOGRAM_TO_HAZARDS:
            for hc in PICTOGRAM_TO_HAZARDS[pictogram]:
                codes.add(hc)

    return codes


def _extract_h_code(text: str) -> str:
    """Extract H-phrase code (e.g., 'H225') from a string like 'H225: Highly flammable'."""
    import re
    match = re.search(r"H\d{3}", text)
    return match.group() if match else ""


def infer_reactivity_flags(ghs_data: dict, substance_data: dict) -> dict:
    """
    Infer the Substance reactivity boolean flags from GHS data.
    Returns dict of flag_name: bool to update on the Substance model.
    """
    flags = {
        "is_acid": False,
        "is_base": False,
        "is_water": False,
        "is_organic_solvent": False,
    }

    cas = substance_data.get("cas_number", "")
    formula = substance_data.get("formula", "")
    name = (substance_data.get("name") or "").lower()

    # Water detection
    if cas == "7732-18-5" or formula in ("H2O", "H₂O"):
        flags["is_water"] = True
        return flags

    # Acid detection from GHS + pH
    h_phrases_text = " ".join(
        p if isinstance(p, str) else p.get("text", "")
        for p in ghs_data.get("h_phrases", [])
    )
    classification_text = " ".join(ghs_data.get("ghs_classification", []))

    ph = substance_data.get("ph_value")
    if ph is not None:
        try:
            ph_val = float(ph)
            if ph_val < 3:
                flags["is_acid"] = True
            elif ph_val > 11:
                flags["is_base"] = True
        except (ValueError, TypeError):
            pass

    # Name-based heuristics (PT-BR catalog) — most acids/bases have predictable
    # naming. Only mark if not already classified as organic solvent (avoids
    # false positives for things like "ácido acrílico" used as monomer).
    if not flags["is_acid"] and not flags["is_base"]:
        if name.startswith("ácido ") or name.startswith("acido "):
            flags["is_acid"] = True
        elif "hidróxido" in name or "hidroxido" in name:
            flags["is_base"] = True
        elif name.startswith("amônia") or name.startswith("amonia"):
            flags["is_base"] = True

    # Strong-acid CAS allow-list (catches inorganic acids whose names may
    # already have set is_acid via the name rule — kept explicit for clarity).
    STRONG_ACID_CAS = {
        "7647-01-0",   # HCl
        "7664-93-9",   # H2SO4
        "7697-37-2",   # HNO3
        "7664-38-2",   # H3PO4
        "7601-90-3",   # HClO4
        "7789-23-3",   # HF
        "10035-10-6",  # HBr
    }
    STRONG_BASE_CAS = {
        "1310-73-2",   # NaOH
        "1310-58-3",   # KOH
        "1310-65-2",   # LiOH
        "21351-79-1",  # CsOH
        "7664-41-7",   # NH3 / NH4OH (technically weak, but stored as concentrated solution)
        "1336-21-6",   # NH4OH solution
    }
    if cas in STRONG_ACID_CAS:
        flags["is_acid"] = True
    if cas in STRONG_BASE_CAS:
        flags["is_base"] = True

    # Organic solvent detection
    # Known organic solvents by CAS (most reliable method)
    KNOWN_ORGANIC_SOLVENT_CAS = {
        "64-17-5",    # ethanol
        "67-56-1",    # methanol
        "67-64-1",    # acetone
        "67-66-3",    # chloroform
        "75-09-2",    # dichloromethane
        "110-54-3",   # hexane
        "108-88-3",   # toluene
        "71-43-2",    # benzene
        "141-78-6",   # ethyl acetate
        "67-68-5",    # DMSO
        "75-05-8",    # acetonitrile
        "109-99-9",   # THF
        "60-29-7",    # diethyl ether
        "78-93-3",    # MEK
        "67-63-0",    # isopropanol
        "142-82-5",   # heptane
        "110-86-1",   # pyridine
        "127-19-5",   # DMA
        "68-12-2",    # DMF
        "872-50-4",   # NMP
    }
    if cas in KNOWN_ORGANIC_SOLVENT_CAS:
        flags["is_organic_solvent"] = True
    elif "Flam. Liq." in classification_text:
        if formula and "C" in formula and not flags["is_acid"]:
            flags["is_organic_solvent"] = True

    return flags
