"""
Custom tags and filters
"""

from datetime import datetime
from django.template import Library
from django.template.defaultfilters import stringfilter
from typing import Literal
register = Library()


@register.filter(is_safe = False)
@stringfilter #Auto convert input value to string
def cut_email(value: str, *args) -> str:
    """
    Cut last character of email if it is too long
    """

    if len(value) > 24:
        return f"{value[:24]}..."
    return value



@register.filter(is_safe = True, expects_localtime = True)
def cut_date(date: datetime, *args) -> str:
    """
    Remove hours/minutes/seconds from date
    """
    return date.strftime("%d %B %Y")


@register.filter(is_safe = True)
def check_length(value, *args):
    return len(str(value))


@register.filter(is_safe = True)
def email2name(email: str, *args) -> str:
    """
    Convert email to name and surname

    :parameter:
        email: Email address

    :return
        Name + Surname
    """

    #Extract names from email
    names = email.split('@')[0].split('.')

    #Build name and surname
    name_surname = ' '.join([name.capitalize() for name in names])

    #Cut if required
    if len(name_surname) > 24:
        name_surname = f"{name_surname[:24]}..."

    return name_surname


@register.simple_tag
def version(*args):
    return '-'.join(args)

@register.simple_tag
def join_args(delimiter: str, *args):
    return str(delimiter).join(args)

@register.inclusion_tag('apps_tag.html', takes_context = True)
def apps_list(context: dict, view_name: str):
    """
    Display container with applications.

    :parameter
        context: context from view
        view_name: todo
    """
    context['view_name'] = view_name
    return context




@register.inclusion_tag('topbar__tag.html', takes_context = True)
def topbar(context: dict, show_searchbar: Literal['yes', 'no'] = 'yes'):
    """
    Display topbar.

    :parameter
        context: context from view
        show_searchbar: indicate if topbar should include searchbar
    """
    context['show_searchbar'] = show_searchbar
    return context


@register.inclusion_tag('base__tag.html', takes_context = True)
def base(context: dict, show_searchbar: Literal['yes', 'no'] = 'yes'):
    """
    Base for each page.

    :parameter
        context: context from view
        show_searchbar: indicate if topbar should include searchbar
    """
    context['show_searchbar'] = show_searchbar
    return context


