import os
from csv import DictReader

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredients

ingredients_file = os.path.join(
    settings.BASE_DIR,
    './data/ingredients.csv'
)


class Command(BaseCommand):
    """Загрузка базы из готовых *.csv файлов."""
    help = "Загрузка данных в базу данных из файлов *.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            '--ingredients',
            action='store_true',
            help='Загрузка данных в базу данных из файла ingredients.csv'
        )
        parser.add_argument(
            '--import_all',
            action='store_true',
            help='Загрузка данных в базу данных во все таблицы.'
        )

    def import_ingredients(self):
        """Получение и сохранение данных из определенных файлов."""

        if Ingredients.objects.exists():
            print('Данные в ingredients уже загружены. Аварийное завершение.')
        else:
            print('Загрузка данных в ingredients.')

            for row in DictReader(
                open(
                    ingredients_file,
                    encoding='utf-8-sig'
                )
            ):
                ingredients = Ingredients(
                    name=row['name'],
                    measurement_unit=row['measurement_unit'],
                )
                ingredients.save()

            print('Загрузка данных в ingredients завершена.')

    def handle(self, **options):
        """Команда для выбора базы для загрузки."""

        if options['ingredients']:
            self.import_ingredients()

        if options['import_all']:
            self.import_ingredients()
