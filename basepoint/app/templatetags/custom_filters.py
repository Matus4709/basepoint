from django import template

register = template.Library()

@register.filter
def format_currency(value):
    if value is None:
        return ''
    return f"{value:,.2f} PLN".replace(',', ' ').replace('.', ',')
