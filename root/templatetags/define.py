from typing import Any
from django import template


register = template.Library()


@register.simple_tag
def define(value: Any) -> Any:
	return value
