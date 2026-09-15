from django.contrib import admin, messages

from .ai import generate_summary
from .models import Brand, Category, Product, Purchase, Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'category', 'status', 'user', 'created_at')
    list_filter = ('status', 'category', 'brand')
    search_fields = ('title', 'brand__title')
    actions = ('approve', 'hide', 'write_summary')

    @admin.action(description='Сгенерировать краткое описание')
    def write_summary(self, request, queryset):
        for product in queryset.select_related('brand', 'category'):
            try:
                product.summary = generate_summary(product)
            except Exception as error:
                self.message_user(request, f'{product}: {error}', messages.ERROR)
                return
            product.save(update_fields=['summary'])
        self.message_user(request, 'Готово. Прочитайте описания перед публикацией.')

    @admin.action(description='Опубликовать')
    def approve(self, request, queryset):
        updated = queryset.update(status=Product.PUBLISHED)
        self.message_user(request, f'Опубликовано товаров: {updated}')

    @admin.action(description='Снять с публикации')
    def hide(self, request, queryset):
        updated = queryset.update(status=Product.DRAFT)
        self.message_user(request, f'Снято с публикации: {updated}')


admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Purchase)
admin.site.register(Review)
