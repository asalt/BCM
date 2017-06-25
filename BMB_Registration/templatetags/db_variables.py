from django import template
from BMB_Registration.models import Variable

register = template.Library()


@register.simple_tag
def get_variable(variable):

    try:
        return Variable.objects.get(variable_name=variable).variable_value
        
    except Exception as e:

        print(e, variable)

        return ''
