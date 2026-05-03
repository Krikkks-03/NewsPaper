from .models import Category

def categories_processor(request):
    """Добавляет список категорий в контекст всех шаблонов"""
    return {
        'categories': Category.objects.all()
    }