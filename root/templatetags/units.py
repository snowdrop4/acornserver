from django import template

register = template.Library()

@register.filter
def IEC_80000_13(size: int | float) -> str:
	if abs(size) < 1024.0:
		return '{} {}'.format(size, 'B')
	
	size /= 1024.0
	for unit in ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB']:
		if abs(size) < 1024.0:
			return '{:.2f} {}'.format(size, unit)
		size /= 1024.0
		
	return '{:.2f} {}'.format(size, 'YiB')
