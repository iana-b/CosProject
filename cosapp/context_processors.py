from .models import Category, Brand

def categories_processor(request):
    """
    Context processor to add categories and brands to all templates
    """
    categories = Category.objects.order_by("title")
    brands = Brand.objects.order_by("title")
    return {'categories': categories, 'brands': brands} 