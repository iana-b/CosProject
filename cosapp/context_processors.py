from .models import Category, Brand


def categories_processor(request):
    """
    Context processor to add categories and brands to all templates
    """
    categories = Category.objects.all()
    brands = Brand.objects.all()
    return {'categories': categories, 'brands': brands}
