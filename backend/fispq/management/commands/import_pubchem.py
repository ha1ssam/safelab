"""
Management command: import substances from PubChem.

Usage:
    # Import from the built-in lab catalog (~50 common reagents)
    python manage.py import_pubchem --catalog

    # Import a single substance by CAS
    python manage.py import_pubchem --cas 64-17-5

    # Import a single substance by name
    python manage.py import_pubchem --name "sulfuric acid"

    # Import from a JSON file
    python manage.py import_pubchem --file substances.json

The JSON file format:
    [{"cas": "64-17-5", "name": "Etanol"}, ...]
"""

import json

from django.core.management.base import BaseCommand, CommandError

from fispq.services.importer import SubstanceImporter
from fispq.services.lab_catalog import LAB_CATALOG


class Command(BaseCommand):
    help = "Importa substâncias do PubChem para o banco de dados local."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--catalog",
            action="store_true",
            help="Importa o catálogo embutido de reagentes comuns de laboratório.",
        )
        group.add_argument(
            "--cas",
            type=str,
            help="Importa uma substância pelo número CAS.",
        )
        group.add_argument(
            "--name",
            type=str,
            help="Importa uma substância pelo nome (busca no PubChem).",
        )
        group.add_argument(
            "--file",
            type=str,
            help="Importa de um arquivo JSON (lista de {cas, name}).",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas mostra o que seria importado, sem gravar.",
        )

    def handle(self, *args, **options):
        importer = SubstanceImporter()

        if options["catalog"]:
            self._import_catalog(importer, options["dry_run"])
        elif options["cas"]:
            self._import_single_cas(importer, options["cas"], options["dry_run"])
        elif options["name"]:
            self._import_single_name(importer, options["name"], options["dry_run"])
        elif options["file"]:
            self._import_from_file(importer, options["file"], options["dry_run"])

    def _import_catalog(self, importer: SubstanceImporter, dry_run: bool):
        self.stdout.write(
            self.style.NOTICE(
                f"Importando catálogo de laboratório ({len(LAB_CATALOG)} substâncias)..."
            )
        )

        if dry_run:
            for item in LAB_CATALOG:
                self.stdout.write(f"  [dry-run] {item['name']} (CAS: {item.get('cas', 'N/A')})")
            return

        result = importer.bulk_import(LAB_CATALOG)
        self.stdout.write(self.style.SUCCESS(f"\n{result.summary()}"))

        if result.errors:
            self.stdout.write(self.style.ERROR("\nErros:"))
            for identifier, error in result.errors:
                self.stdout.write(f"  - {identifier}: {error}")

    def _import_single_cas(self, importer: SubstanceImporter, cas: str, dry_run: bool):
        self.stdout.write(f"Buscando CAS {cas} no PubChem...")

        if dry_run:
            self.stdout.write(f"  [dry-run] Importaria CAS: {cas}")
            return

        substance = importer.import_by_cas(cas)
        if substance:
            self.stdout.write(self.style.SUCCESS(f"Importado: {substance.name}"))
        else:
            raise CommandError(f"Não foi possível importar CAS {cas}")

    def _import_single_name(self, importer: SubstanceImporter, name: str, dry_run: bool):
        self.stdout.write(f"Buscando '{name}' no PubChem...")

        if dry_run:
            self.stdout.write(f"  [dry-run] Importaria: {name}")
            return

        substance = importer.import_by_name(name)
        if substance:
            self.stdout.write(self.style.SUCCESS(f"Importado: {substance.name}"))
        else:
            raise CommandError(f"Não foi possível importar '{name}'")

    def _import_from_file(self, importer: SubstanceImporter, filepath: str, dry_run: bool):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                compounds = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise CommandError(f"Erro ao ler arquivo: {e}")

        if not isinstance(compounds, list):
            raise CommandError("O arquivo deve conter uma lista JSON de objetos.")

        self.stdout.write(f"Importando {len(compounds)} substâncias do arquivo...")

        if dry_run:
            for item in compounds:
                self.stdout.write(f"  [dry-run] {item.get('name', item.get('cas', '?'))}")
            return

        result = importer.bulk_import(compounds)
        self.stdout.write(self.style.SUCCESS(f"\n{result.summary()}"))
