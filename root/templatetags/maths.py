from django import template


register = template.Library()


@register.simple_tag
def divide(numerator, denominator):
	if numerator == 0 or denominator == 0:
		return "∞"
	
	return str(numerator / denominator)


@register.simple_tag
def multiply(x1, x2):
	return str(x1 * x2)
