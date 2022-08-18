from typing import Any
from django import template


register = template.Library()


@register.simple_tag
def print(value: Any) -> Any:
	print(str(value))
	return value
