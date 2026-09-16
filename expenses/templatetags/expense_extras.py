from django import template

register = template.Library()

ICONS = {
    'еда': '🍔',
    'транспорт': '🚗',
    'жильё': '🏠',
    'развлечения': '🎬',
    'здоровье': '💊',
    'одежда': '👕',
    'связь и интернет': '📱',
    'прочее': '📦',
}

@register.filter
def category_icon(name):
    if not name:
        return '💳'
    return ICONS.get(name.strip().lower(), '💳')