# myapp/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def format_vnd(value):
    try:
        # Convert the value to an integer
        value = int(value)
        # Return formatted string with thousands separators
        return f"{value:,.0f} VNĐ"
    except (ValueError, TypeError):
        # If the value can't be converted to an integer, return the original value
        return value
