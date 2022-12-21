import os

from csv import DictReader
from django.core.management import BaseCommand
from django.conf import settings

from recipes.models import Ingredients


ingredients_file = os.path.join(
    settings.BASE_DIR,
    '../data/ingredients.csv'
)


class Command(BaseCommand):
    """Загрузка БД из готовых *.csv файлов."""
    # Подсказка когда пользователь пишет help.
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
        # Если данные не пустые повторно не загружаем.
        if Ingredients.objects.exists():
            print('Данные в category уже загружены. Аварийное завершение.')
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
        if options['ingredients']:
            self.import_ingredients()
        if options['import_all']:
            self.import_ingredients()
