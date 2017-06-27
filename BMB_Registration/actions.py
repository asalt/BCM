import csv
from django.http import HttpResponse
from django.shortcuts import redirect

from BMB_Registration.models import User
from BMB_Registration.models import Submission


def export_as_csv_action(description="Export selected objects as CSV file",
                         output_name='download',
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta

        if not fields:
            field_names = [field.name for field in opts.fields]
        else:
            field_names = fields

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(output_name)

        writer = csv.writer(response)
        if header:
            writer.writerow(field_names)
        for obj in queryset:
            row = [getattr(obj, field)() if callable(getattr(obj, field)) else getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response
    export_as_csv.short_description = description
    return export_as_csv


# def assign_poster_numbers():

#     # def inner(modeladmin, request, queryset):
#     def inner(modeladmin, request, queryset):  # we don't actually need these
#         users = User.objects.order_by('last_name').filter(presentation='poster')

#         for number, user in enumerate(users, 1):

#             try:
#                 submission = Submission.objects.get(user=user)

#             except Exception as e:

#                 continue

#             submission.poster_number = number

#             submission.save()

#         return redirect(request.path)
#     inner_func = inner
#     inner_func.short_description = 'Assign Poster Numbers'
#     return inner_func
