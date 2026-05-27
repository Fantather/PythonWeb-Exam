import uuid
from django.utils.text import slugify
from django.db.models import Model
from unidecode import unidecode

def generate_unique_slug(title: str, model_class: type[Model], base_default: str = "node") -> str:
    """
    Генерирует уникальный slug на основе переданной строки.
    Выполняет проверку на совпадения в БД, так что он будет уникальным.
    """
    base_slug = slugify(unidecode(title)) or base_default
    slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
    
    while model_class.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
        
    return slug