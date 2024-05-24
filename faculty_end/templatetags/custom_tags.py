from django import template

register = template.Library()

@register.filter
def set_evidence_count(value):
    return value
