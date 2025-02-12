
from django import template

register = template.Library()

@register.filter
def format_vnd(value):
    try:
        value = int(value)
        return f"{value:,.0f} VNĐ"
    except (ValueError, TypeError):
        return value
