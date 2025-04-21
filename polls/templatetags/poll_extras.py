from django import template

register = template.Library()

@register.filter
def div(value, arg):
    try:
        return (value / arg) if arg != 0 else 0
    except:
        return 0

@register.filter
def mul(value, arg):
    try:
        return value * arg
    except:
        return 0

@register.filter
def total_votes(choices):
    return sum(choice.votes for choice in choices)
