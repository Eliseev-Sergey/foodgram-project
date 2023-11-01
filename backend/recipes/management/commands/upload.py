import csv
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    _file_path = os.path.join('data', 'ingredients.csv')

    def handle(self, *args, **options):
        if Ingredient.objects.exists():
            self.stdout.write(self.style.WARNING('Данные уже существуют'))
            return

        with open(self._file_path, encoding='UTF-8') as file:
            reader = csv.reader(file)
            next(reader)

            ingredients = [
                Ingredient(name=name, measurement_unit=measurement_unit)
                for name, measurement_unit in reader
            ]

            Ingredient.objects.bulk_create(ingredients)

        self.stdout.write(
            self.style.SUCCESS('Данные успешно импортированы!')
        )
