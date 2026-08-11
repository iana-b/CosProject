from django.contrib import admin
from .models import Brand, Category, Product, Purchase, Review, PageView


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'category', 'status', 'user', 'created_at')
    list_filter = ('status', 'category', 'brand')
    search_fields = ('title', 'brand__title')
    actions = ('approve', 'hide')

    @admin.action(description='Опубликовать')
    def approve(self, request, queryset):
        updated = queryset.update(status=Product.PUBLISHED)
        self.message_user(request, f'Опубликовано товаров: {updated}')

    @admin.action(description='Снять с публикации')
    def hide(self, request, queryset):
        updated = queryset.update(status=Product.DRAFT)
        self.message_user(request, f'Снято с публикации: {updated}')


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'path', 'product', 'user')
    list_filter = ('created_at',)
    readonly_fields = ('path', 'product', 'user', 'ip_hash', 'created_at')

    def has_add_permission(self, request):
        return False


admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Purchase)
admin.site.register(Review)
