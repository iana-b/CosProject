from django.core.management.base import BaseCommand

from cosapp.ai import generate_summary
from cosapp.models import Product


class Command(BaseCommand):
    help = 'Генерирует краткие описания для товаров, у которых их ещё нет.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, help='Сколько товаров обработать за раз')
        parser.add_argument('--dry-run', action='store_true', help='Показать результат, ничего не сохраняя')

    def handle(self, *args, **options):
        products = Product.objects.filter(summary='').select_related('brand', 'category')
        if options['limit']:
            products = products[:options['limit']]
        for product in products:
            summary = generate_summary(product)
            self.stdout.write(f'\n{product.brand} {product.title}\n{summary}')
            if not options['dry_run']:
                product.summary = summary
                product.save(update_fields=['summary'])
