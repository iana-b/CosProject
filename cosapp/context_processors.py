from .models import Category, Brand

# Загружаем один раз при первом запросе, дальше из памяти. Категории/бренды в шапке не меняются.
_header_nav = None


def categories_processor(request):
    global _header_nav
    if _header_nav is None:
        _header_nav = {
            "categories": list(Category.objects.all()),
            "brands": list(Brand.objects.all()),
        }
    return {"categories": _header_nav["categories"], "brands": _header_nav["brands"]}
