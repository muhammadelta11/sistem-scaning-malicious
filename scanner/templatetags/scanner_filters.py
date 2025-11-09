"""
Custom template filters untuk scanner app.
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Mengakses dictionary dengan key yang bisa mengandung tanda minus atau karakter khusus.
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, None)
    return None


@register.filter
def get_item_index(category_index, categories):
    """
    Hitung global index untuk item berdasarkan category index.
    """
    if not isinstance(categories, dict):
        return 0
    
    total = 0
    category_list = list(categories.values())
    
    for i, cat in enumerate(category_list):
        if i < category_index:
            total += len(cat.get('items', []))
    
    return total


@register.simple_tag(takes_context=True)
def calculate_item_global_index(context, category_index, item_index):
    """
    Calculate global index untuk item.
    
    Usage:
    {% calculate_item_global_index forloop.parentloop.counter0 forloop.counter0 as item_index %}
    """
    results = context.get('results', {})
    categories = results.get('categories', {})
    
    if not isinstance(categories, dict):
        return 0
    
    total = 0
    category_list = list(categories.values())
    
    # Hitung jumlah items di kategori sebelumnya
    try:
        category_index_int = int(category_index)
        item_index_int = int(item_index)
        
        for i in range(category_index_int):
            if i < len(category_list):
                total += len(category_list[i].get('items', []))
        
        # Tambahkan index item di kategori saat ini
        total += item_index_int
        
    except (ValueError, TypeError):
        return 0
    
    return total

