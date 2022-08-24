from django import template

register = template.Library()


@register.filter
def remove_page_from_query_string(qs: dict) -> str:
    return "&".join([f"{a}={b}" for (a, b) in qs.items() if a != "page"])


# Given both the current page number and the total number of pages,
#   returns a list of page numbers to be displayed in page navigation.
#
# Provided the total number of pages is more than 11, the returned list
#   will always be 11 elements long, regardless of the position of the
#   current page (marked with `^` in the following example):
#
# [45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55]
#                                      ^^
#
# [28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]
#                      ^^
#
# [1,  2,  3,  4,  5,  6,  7,  8,  9,  10, 11]
#  ^
#
# Thus, the user can always see 11 pages regardless of their proximity
#  to the start or the end of the list of pages.
@register.simple_tag
def generate_pagination_page_list(current_page: int, total_pages: int) -> list[int]:
    m = list(range(max(current_page - 5, 1), min(current_page + 5, total_pages) + 1))

    remainder = 11 - len(m)

    l = []
    r = []

    if remainder > 0:
        l = list(range(max(m[0] - remainder, 1), m[0]))
        r = list(range(m[-1] + 1, min(m[-1] + remainder + 1, total_pages)))

    return l + m + r
