from .models import Category, Brand


def categories_processor(request):
    return {"categories": Category.objects.all(), "brands": Brand.objects.all()}
