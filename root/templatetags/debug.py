from django import template


register = template.Library()


@register.simple_tag
def print(a):
	print(str(a))
	return a
