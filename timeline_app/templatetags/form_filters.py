from django import template

register = template.Library()

@register.filter(name='addclass')
def addclass(field, css_class):
    return field.as_widget(attrs={'class': css_class})