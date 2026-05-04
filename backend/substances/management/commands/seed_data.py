"""
Seed initial data: hazards, substances, and a few curated compatibility records.

Usage:
    python manage.py seed_data
    python manage.py seed_data --reset   # wipe before seeding

Idempotent — running it twice without --reset only inserts missing rows.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from hazards.models import Hazard
from substances.models import Substance
from compatibility.models import CompatibilityRecord


HAZARDS = [
    ("flammable",       "Inflamável",                  "high",   "flame"),
    ("corrosive",       "Corrosivo",                   "high",   "test-tube"),
    ("toxic",           "Tóxico",                      "high",   "skull"),
    ("oxidizer",        "Oxidante",                    "high",   "flame"),
    ("reactive_water",  "Reage com água",              "high",   "droplet-off"),
    ("explosive",       "Explosivo",                   "high",   "alert-octagon"),
    ("irritant",        "Irritante",                   "medium", "alert-triangle"),
    ("carcinogen",      "Carcinogênico",               "high",   "biohazard"),
    ("env_hazard",      "Perigoso ao meio ambiente",   "medium", "leaf"),
    ("compressed_gas",  "Gás comprimido",              "medium", "wind"),
]


SUBSTANCES = [
    {
        "name": "Água destilada",
        "formula": "H2O",
        "cas_number": "7732-18-5",
        "physical_state": "liquid",
        "ph_value": "7.00",
        "molar_mass": "18.015",
        "is_water": True,
        "description": "Solvente universal usado em diluições e preparo de soluções.",
        "required_ppe": ["óculos de proteção"],
        "handling_notes": "Manipulação trivial; verificar pureza para análises sensíveis.",
        "storage_instructions": "Recipiente fechado, ao abrigo de contaminação.",
        "hazards": [],
    },
    {
        "name": "Ácido clorídrico (HCl)",
        "formula": "HCl",
        "cas_number": "7647-01-0",
        "physical_state": "aqueous",
        "ph_value": "1.00",
        "molar_mass": "36.460",
        "is_acid": True,
        "description": "Ácido forte mineral; comum em titulações e limpeza de vidraria.",
        "required_ppe": ["luvas nitrílicas", "óculos de proteção", "jaleco", "máscara para vapores"],
        "handling_notes": "Manipular SEMPRE em capela. Adicionar à água, nunca o contrário.",
        "critical_alerts": "Vapores irritantes e corrosivos — risco respiratório severo.",
        "storage_instructions": "Frasco âmbar, lacrado, em local ventilado e longe de bases.",
        "storage_incompatibilities": "Bases fortes, oxidantes (permanganatos, cloratos), metais reativos.",
        "hazards": ["corrosive", "irritant", "toxic"],
    },
    {
        "name": "Hidróxido de sódio (NaOH)",
        "formula": "NaOH",
        "cas_number": "1310-73-2",
        "physical_state": "solid",
        "ph_value": "14.00",
        "molar_mass": "39.997",
        "is_base": True,
        "description": "Base forte (soda cáustica); usado em preparo de soluções básicas.",
        "required_ppe": ["luvas nitrílicas", "óculos de proteção", "jaleco"],
        "handling_notes": "Dissolução é altamente exotérmica — adicionar lentamente à água gelada.",
        "critical_alerts": "Causa queimaduras químicas graves no contato com a pele.",
        "storage_instructions": "Frasco plástico bem vedado; longe de ácidos e umidade.",
        "storage_incompatibilities": "Ácidos fortes, alumínio, zinco.",
        "hazards": ["corrosive"],
    },
    {
        "name": "Ácido sulfúrico (H2SO4)",
        "formula": "H2SO4",
        "cas_number": "7664-93-9",
        "physical_state": "liquid",
        "ph_value": "0.30",
        "molar_mass": "98.079",
        "is_acid": True,
        "description": "Ácido forte diprótico, oxidante a quente; muito usado em laboratório.",
        "required_ppe": ["luvas nitrílicas", "face shield", "avental de PVC", "óculos de proteção"],
        "handling_notes": "Manipular em capela. SEMPRE adicionar o ácido à água.",
        "critical_alerts": "Reação violentíssima com água em quantidade desproporcional.",
        "storage_instructions": "Frasco resistente a ácidos, ventilado, longe de bases e materiais orgânicos.",
        "storage_incompatibilities": "Bases, metais alcalinos, materiais orgânicos, oxidantes.",
        "hazards": ["corrosive", "toxic", "oxidizer"],
    },
    {
        "name": "Etanol",
        "formula": "C2H6O",
        "cas_number": "64-17-5",
        "physical_state": "liquid",
        "molar_mass": "46.069",
        "is_organic_solvent": True,
        "description": "Álcool etílico; solvente orgânico polar e desinfetante.",
        "required_ppe": ["óculos de proteção", "luvas"],
        "handling_notes": "Manter longe de chamas e fontes de ignição.",
        "critical_alerts": "Altamente inflamável — vapores podem formar misturas explosivas.",
        "storage_instructions": "Local ventilado, fresco, longe de oxidantes e fontes de calor.",
        "storage_incompatibilities": "Oxidantes fortes (permanganatos, peróxidos, ácido nítrico).",
        "hazards": ["flammable", "irritant"],
    },
    {
        "name": "Acetona",
        "formula": "C3H6O",
        "cas_number": "67-64-1",
        "physical_state": "liquid",
        "molar_mass": "58.080",
        "is_organic_solvent": True,
        "description": "Cetona simples; solvente orgânico volátil.",
        "required_ppe": ["óculos de proteção", "luvas nitrílicas"],
        "handling_notes": "Manipular em capela ou área bem ventilada.",
        "critical_alerts": "Extremamente inflamável; vapores mais densos que o ar.",
        "storage_instructions": "Frasco fechado, longe de calor e oxidantes.",
        "storage_incompatibilities": "Oxidantes fortes, ácidos concentrados.",
        "hazards": ["flammable", "irritant"],
    },
    {
        "name": "Permanganato de potássio (KMnO4)",
        "formula": "KMnO4",
        "cas_number": "7722-64-7",
        "physical_state": "solid",
        "molar_mass": "158.034",
        "description": "Oxidante forte; usado em titulometria e desinfecção.",
        "required_ppe": ["luvas nitrílicas", "óculos de proteção", "jaleco"],
        "handling_notes": "Evitar contato com materiais orgânicos.",
        "critical_alerts": "Pode provocar ignição espontânea em contato com glicerina ou álcool.",
        "storage_instructions": "Frasco fechado, em local seco, separado de orgânicos e redutores.",
        "storage_incompatibilities": "Solventes orgânicos, glicerina, ácidos concentrados.",
        "hazards": ["oxidizer", "corrosive", "env_hazard"],
    },
    {
        "name": "Peróxido de hidrogênio 30% (H2O2)",
        "formula": "H2O2",
        "cas_number": "7722-84-1",
        "physical_state": "liquid",
        "molar_mass": "34.014",
        "description": "Oxidante; em laboratório usado em soluções até 30%.",
        "required_ppe": ["luvas nitrílicas", "óculos de proteção", "face shield"],
        "handling_notes": "Manipular em recipiente plástico ou vidro neutro; evitar contaminação.",
        "critical_alerts": "Decomposição catalítica libera O2 e calor — risco de explosão se confinado.",
        "storage_instructions": "Frasco ventilado, ao abrigo de luz e calor.",
        "storage_incompatibilities": "Metais (ferro, cobre), orgânicos, redutores.",
        "hazards": ["oxidizer", "corrosive", "irritant"],
    },
    {
        "name": "Hipoclorito de sódio (NaClO)",
        "formula": "NaClO",
        "cas_number": "7681-52-9",
        "physical_state": "aqueous",
        "ph_value": "12.50",
        "molar_mass": "74.440",
        "is_base": True,
        "description": "Solução desinfetante (água sanitária ~2,5%); oxidante.",
        "required_ppe": ["luvas nitrílicas", "óculos de proteção"],
        "handling_notes": "Trabalhar em área ventilada.",
        "critical_alerts": "Mistura com ácidos ou amoniacais libera Cl2 / cloraminas tóxicos.",
        "storage_instructions": "Frasco opaco, fechado, longe de ácidos e calor.",
        "storage_incompatibilities": "Ácidos, amoníaco, redutores.",
        "hazards": ["corrosive", "oxidizer", "toxic"],
    },
    {
        "name": "Sódio metálico (Na)",
        "formula": "Na",
        "cas_number": "7440-23-5",
        "physical_state": "solid",
        "molar_mass": "22.990",
        "description": "Metal alcalino reativo; usado em síntese e secagem de solventes.",
        "required_ppe": ["luvas nitrílicas", "óculos de proteção", "face shield", "luvas térmicas"],
        "handling_notes": "Cortar e manipular sob óleo mineral. NUNCA em contato com água.",
        "critical_alerts": "Reage violentamente com água formando H2 (inflamável) e NaOH.",
        "storage_instructions": "Submerso em querosene ou óleo mineral, em frasco hermético.",
        "storage_incompatibilities": "Água, álcoois, halogenados, ácidos.",
        "hazards": ["reactive_water", "flammable", "corrosive"],
    },
    {
        "name": "Ácido nítrico (HNO3)",
        "formula": "HNO3",
        "cas_number": "7697-37-2",
        "physical_state": "liquid",
        "ph_value": "1.00",
        "molar_mass": "63.013",
        "is_acid": True,
        "description": "Ácido forte e oxidante poderoso.",
        "required_ppe": ["luvas nitrílicas", "face shield", "avental de PVC"],
        "handling_notes": "Manipular em capela. Diluir adicionando o ácido à água.",
        "critical_alerts": "Vapores nitrosos altamente tóxicos; reage explosivamente com orgânicos.",
        "storage_instructions": "Frasco resistente, ventilado, longe de orgânicos e bases.",
        "storage_incompatibilities": "Bases, orgânicos (etanol, acetona), metais reativos.",
        "hazards": ["corrosive", "oxidizer", "toxic"],
    },
    {
        "name": "Amônia (NH3) solução",
        "formula": "NH3 (aq)",
        "cas_number": "7664-41-7",
        "physical_state": "aqueous",
        "ph_value": "11.60",
        "molar_mass": "17.031",
        "is_base": True,
        "description": "Solução amoniacal (hidróxido de amônio); base fraca.",
        "required_ppe": ["luvas nitrílicas", "óculos de proteção", "máscara para vapores"],
        "handling_notes": "Manipular em capela.",
        "critical_alerts": "Vapores irritantes; com hipoclorito forma cloraminas tóxicas.",
        "storage_instructions": "Frasco fechado, ventilado, longe de ácidos.",
        "storage_incompatibilities": "Ácidos, halogenados, hipoclorito.",
        "hazards": ["corrosive", "toxic", "irritant"],
    },
]


# Curated, explicit compatibility records (substance names — order doesn't matter).
RECORDS = [
    # (a, b, status, risk, reaction_type, notes)
    (
        "Hipoclorito de sódio (NaClO)", "Ácido clorídrico (HCl)",
        "unsafe", "high", "Liberação de Cl2 (gás cloro) tóxico",
        "Mistura clássica perigosa. Libera gás cloro extremamente tóxico ao sistema respiratório.",
    ),
    (
        "Hipoclorito de sódio (NaClO)", "Amônia (NH3) solução",
        "unsafe", "high", "Formação de cloraminas",
        "Cloraminas são gases tóxicos e irritantes — risco de edema pulmonar.",
    ),
    (
        "Permanganato de potássio (KMnO4)", "Etanol",
        "unsafe", "high", "Reação oxidativa — risco de ignição",
        "Oxidação violenta do álcool. Pode haver ignição espontânea.",
    ),
    (
        "Peróxido de hidrogênio 30% (H2O2)", "Acetona",
        "unsafe", "high", "Formação de peróxido de acetona (TATP) — explosivo",
        "Reação extremamente perigosa. JAMAIS misturar.",
    ),
    (
        "Ácido nítrico (HNO3)", "Etanol",
        "unsafe", "high", "Nitração / oxidação violenta",
        "Reação altamente exotérmica e potencialmente explosiva.",
    ),
    (
        "Sódio metálico (Na)", "Água destilada",
        "unsafe", "high", "Liberação de H2 + calor",
        "Reação extremamente violenta. NUNCA expor sódio metálico à água.",
    ),
    (
        "Ácido sulfúrico (H2SO4)", "Hidróxido de sódio (NaOH)",
        "unsafe", "high", "Neutralização exotérmica violenta",
        "Reação ácido-base muito energética; risco de respingos. Diluir ambos antes.",
    ),
    (
        "Etanol", "Água destilada",
        "safe", "low", "Diluição (miscíveis em qualquer proporção)",
        "Combinação rotineira sem risco químico.",
    ),
    (
        "Acetona", "Etanol",
        "safe", "low", "Mistura de solventes orgânicos",
        "Compatíveis. Atenção apenas à inflamabilidade combinada.",
    ),
]


class Command(BaseCommand):
    help = "Popula o banco com dados iniciais (riscos, substâncias e compatibilidades)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Apaga registros existentes antes de inserir.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write(self.style.WARNING("Limpando dados existentes..."))
            CompatibilityRecord.objects.all().delete()
            Substance.objects.all().delete()
            Hazard.objects.all().delete()

        # ─── Hazards ───────────────────────────────────────────────────────
        hazards_by_code: dict[str, Hazard] = {}
        for code, name, severity, pictogram in HAZARDS:
            hazard, _ = Hazard.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "default_severity": severity,
                    "pictogram": pictogram,
                },
            )
            hazards_by_code[code] = hazard
        self.stdout.write(self.style.SUCCESS(f"[ok]{len(hazards_by_code)} riscos cadastrados"))

        # ─── Substances ────────────────────────────────────────────────────
        substances_by_name: dict[str, Substance] = {}
        for raw in SUBSTANCES:
            data = dict(raw)
            hazard_codes = data.pop("hazards", [])
            substance, _ = Substance.objects.update_or_create(
                name=data["name"],
                defaults=data,
            )
            if hazard_codes:
                substance.hazards.set([hazards_by_code[c] for c in hazard_codes])
            substances_by_name[substance.name] = substance
        self.stdout.write(self.style.SUCCESS(f"[ok]{len(substances_by_name)} substâncias cadastradas"))

        # ─── Compatibility records ─────────────────────────────────────────
        count = 0
        for name_a, name_b, status, risk, reaction, notes in RECORDS:
            a = substances_by_name.get(name_a)
            b = substances_by_name.get(name_b)
            if not a or not b:
                self.stdout.write(self.style.WARNING(f"  -pulando: {name_a} x {name_b}"))
                continue
            # Normalize to a.id < b.id (the model's save() does this too, but we
            # do it here so update_or_create finds existing rows correctly).
            if a.id > b.id:
                a, b = b, a
            CompatibilityRecord.objects.update_or_create(
                substance_a=a,
                substance_b=b,
                defaults={
                    "status": status,
                    "risk_level": risk,
                    "reaction_type": reaction,
                    "notes": notes,
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"[ok]{count} registros de compatibilidade"))
        self.stdout.write(self.style.SUCCESS("Seed finalizado."))
