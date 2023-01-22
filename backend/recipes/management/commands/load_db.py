import os
from csv import DictReader

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredients, Tags

ingredients_file = os.path.join(
    settings.BASE_DIR,
    './data/ingredients.csv'
)
tags_file = os.path.join(
    settings.BASE_DIR,
    './data/tags.csv'
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
            '--tags',
            action='store_true',
            help='Загрузка данных в базу данных из файла tags.csv'
        )
        parser.add_argument(
            '--import_all',
            action='store_true',
            help='Загрузка данных в базу данных во все таблицы.'
        )

    def import_ingredients(self):
        """Получение и сохранение данных из ingredients_file."""

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

    def import_tags(self):
        """Получение и сохранение данных из tags_file."""

        if Tags.objects.exists():
            print('Данные в tags уже загружены. Аварийное завершение.')
        else:
            print('Загрузка данных в tags.')

            for row in DictReader(
                open(
                    tags_file,
                    encoding='utf-8-sig'
                )
            ):
                tags = Tags(
                    name=row['name'],
                    color=row['color'],
                    slug=row['slug'],
                )
                tags.save()

            print('Загрузка данных в tags завершена.')

    def handle(self, **options):
        """Команда выбора базы для загрузки."""

        if options['ingredients']:
            self.import_ingredients()

        if options['tags']:
            self.import_tags()

        if options['import_all']:
            self.import_ingredients()
            self.import_tags()
