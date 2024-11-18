from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    existing_classes = field.field.widget.attrs.get('class', '')
    combined_classes = f"{existing_classes} {css}".strip()
    return field.as_widget(attrs={'class': combined_classes})
