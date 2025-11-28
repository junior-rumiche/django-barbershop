from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified parameters added or changed.

    It also removes any empty parameters to keep things clean,
    except when a value is provided in kwargs (even if empty, though usually we want to override).
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()

@register.simple_tag
def get_pagination_range(page_obj, on_each_side=2, on_ends=1):
    return page_obj.paginator.get_elided_page_range(page_obj.number, on_each_side=on_each_side, on_ends=on_ends)