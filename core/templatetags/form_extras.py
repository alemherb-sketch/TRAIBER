from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={'class': css_class})


@register.filter(name='widget_type')
def widget_type(field):
    return field.field.widget.__class__.__name__.lower()
