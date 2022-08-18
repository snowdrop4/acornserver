from django import template


register = template.Library()


@register.simple_tag
def divide(numerator: int | float, denominator: int | float) -> str:
	if numerator == 0 or denominator == 0:
		return "∞"
	
	return str(numerator / denominator)


@register.simple_tag
def multiply(x1: int | float, x2: int | float) -> str:
	return str(x1 * x2)
