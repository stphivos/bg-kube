import os
from django import template

register = template.Library()


@register.simple_tag
def version():
    return os.environ.get('VERSION', '1.0.0')


@register.simple_tag
def env():
    return os.environ.get('ENV', 'dev')


@register.simple_tag
def color():
    return os.environ.get('COLOR', None)
