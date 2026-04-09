from django import template

register = template.Library()


@register.filter
def split(value, delimiter=","):
    return value.split(delimiter)


@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


CATEGORY_ICONS = {
    "мясо": "fa-solid fa-drumstick-bite",
    "рыба": "fa-solid fa-fish",
    "овощи": "fa-solid fa-carrot",
    "фрукты": "fa-solid fa-apple-whole",
    "молочные": "fa-solid fa-cheese",
    "крупы": "fa-solid fa-wheat-awn",
    "специи": "fa-solid fa-pepper-hot",
    "напитки": "fa-solid fa-mug-hot",
    "выпечка": "fa-solid fa-bread-slice",
    "масла": "fa-solid fa-oil-can",
    "сладкое": "fa-solid fa-candy-cane",
    "соусы": "fa-solid fa-bottle-droplet",
}


@register.filter
def days_plural(n):
    """1 день, 2 дня, 5 дней"""
    try:
        n = int(n)
    except (TypeError, ValueError):
        return f"{n} дней"
    mod10, mod100 = n % 10, n % 100
    if mod100 in range(11, 20):
        word = "дней"
    elif mod10 == 1:
        word = "день"
    elif mod10 in (2, 3, 4):
        word = "дня"
    else:
        word = "дней"
    return f"{n} {word}"


@register.filter
def category_icon(category, default="fa-solid fa-basket-shopping"):
    return CATEGORY_ICONS.get(category.lower(), default) if category else default
