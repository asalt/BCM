import os
from pathlib import Path
from functools import update_wrapper, reduce
import operator as op
from tempfile import gettempdir

from django.contrib import admin
from django.contrib.admin import AdminSite, FieldListFilter
from django.urls import reverse
from django.db import models
from django.utils.translation import ugettext_lazy
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.conf.urls import url
from django.contrib import messages
from django.contrib.admin import DateFieldListFilter
from django.core.files.storage import FileSystemStorage
from django.template.response import SimpleTemplateResponse, TemplateResponse



from BMB_Registration.models import *
from BMB_Registration.actions import *
from BMB_Registration.forms import *
from BMB_Registration.valuerangefilter import ValueRangeFilter

admin.site.site_header = 'BMB Retreat Admin'

# class IntFieldListFilter(FieldListFilter):
#     def __init__(self, field, request, params, model, model_admin, field_path):
#         "docstring"

class MyAdmin(admin.ModelAdmin):

    change_list_template = None  # change as desired
    list_display         = None
    export_header        = True


    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        urls = super().get_urls()

        info = self.opts.app_label, self.opts.model_name

        my_urls = [url(r'export_as_csv/$', wrap(self.export_as_csv), name='{}_{}_export_as_csv'.format(*info))]

        return my_urls + urls


    def export_as_csv(self, request):
        """
        This function returns an export csv action
        'fields' and 'exclude' work like in django ModelForm
        'header' is whether or not to output the column names as the first row
        """
        table      = self.model
        # table_name = table.db_table
        table_name = self.opts.model_name

        if table is None:
            #TODO : Warn invalid?
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if self.list_display is None:
            field_names = [field.name for field in self.opts.fields]
        else:
            field_names = self.list_display

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=BMB_Retreat_{}.csv'.format(table_name)
        writer = csv.writer(response)
        if self.export_header:
            writer.writerow(field_names)
        for entry in table.objects.all():
            row = [getattr(entry, field)() if callable(getattr(entry, field))
                   else getattr(entry, field) for field in field_names]
            writer.writerow(row)
        return response

class BulkAdmin(admin.ModelAdmin):

    change_list_template = 'change_list_bulk.html'  # change as desired
    list_display         = None
    entry_name           = 'DEFAULT'
    help_text            = None

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        urls = super().get_urls()

        info = self.opts.app_label, self.opts.model_name

        my_urls = [url(r'bulk_add/$', wrap(self.bulk_add), name='{}_{}_bulk_add'.format(*info))]

        return my_urls + urls


    def bulk_add(self, request):
        """
        """
        if request.method == 'POST':

            myfile = request.FILES.get('myfile')

            if myfile is None:
                messages.warning(request, 'Must select a file for upload first!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            fs = FileSystemStorage(location=gettempdir())
            filename = fs.save(myfile.name, myfile)
            print(filename)
            fullname = fs.path(filename)
            print(fullname)
            if not os.path.exists(fullname):
                messages.error(request, 'Internal server error accessing file.')
            uploaded_file_url = fs.url(filename)
            entries = self.parse_file(fullname)
            self.save_results(entries)

            fs.delete(filename)

            path = Path(request.path)
            redirect = path.parents[0].as_posix()  # go up 1

            messages.success(request, 'Successfully uploaded files')
            return HttpResponseRedirect(redirect)

        return render(request, 'simple_upload.html',
                      context={'entry_name': self.entry_name,
                               'additional_help': self.help_text,
                      }
        )

    def parse_file(self, filename):
        entries = list()
        with open(filename, 'r') as f:
            for line in f:
                entries.append(line)
        return entries

    def save_results(self, entries):
        raise NotImplementedError('Must subclass and implement')


@admin.register(PI)
class PIAdmin(BulkAdmin):

    entry_name = 'PI'
    help_text  = 'Each PI entry should be of form <font color="red">LastName, FirstName</font>'

    list_display = ('last_name', 'first_name')

    search_fields = ('last_name', 'first_name')

    def save_results(self, entries):
        for entry in entries:

            if len(entry) == 0:
                continue

            split = entry.split(',')

            if len(split) == 1:  # invalid format, store all in lastname
                last = split[0].strip()
                first = ''
            elif len(split) >= 2:  # expected format
                last = split[0].strip()
                first = split[1].strip()

            PI.objects.create(last_name=last, first_name=first)

@admin.register(Department)
class DepartmentAdmin(BulkAdmin):

    entry_name = 'Department'

    list_display = ('name',)

    search_fields = ('name',)

    def save_results(self, entries):
        for entry in entries:
            Department.objects.create(name=entry)


@admin.register(User)
class UserAdmin(MyAdmin):

    change_list_template = 'change_list_user.html'
    # change_list_template = 'change_list_ext.html'

    list_display =  ('last_name', 'first_name', 'gender',
                     'department', 'lab', 'position', 'email',
                     'date_registered', 'shirt_size', 'presentation',
                     'funding_source', 'stay_at_hotel', 'share_room',
                     'roommate_pref', 'vegetarian'
                    )

    search_fields = ('last_name', 'first_name', 'gender',
                     'department', 'lab', 'position', 'email',
                     'date_registered', 'shirt_size', 'presentation',
                     'funding_source', 'stay_at_hotel', 'share_room',
                     'roommate_pref', 'vegetarian'
                    )
    actions = [export_as_csv_action('Download Selected',
                                    fields=list_display, output_name='BMB_Registrants')]

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        urls = super().get_urls()
        info = self.opts.app_label, self.opts.model_name

        my_urls = [url(r'assign_judges/$', wrap(self.assign_judges),
                       name='{}_{}_assign_judges'.format(*info)),
        ]

        return my_urls + urls

    def assign_judges(self, request):
        """
        """
        user_dict = dict()
        for user in User.objects.all():
            q = Submission.objects.filter(user=user)
            print(q, q.values)
            d = {'identifier'   : user.email,
                 'lab'          : user.lab,
                 'poster_number': Submission.objects.filter(user=user).poster_number
            }
            print(d)

        # submissions = Submission.objects.filter(user__presentation='poster')
        # for submission in submissions:
        #     scores = submission.scores
        #     tot_scores = len(scores)
        #     score_sum  = reduce(op.add, filter(None, map(maybe_int, scores)))
        #     result = score_sum / len(scores)

        #     submission.avg_score = result
        #     submission.save()

        # # submissions = Submission.objects.exclude(avg_score=None).order_by('avg_score')
        # submissions = Submission.objects.filter(user__presentation='poster').order_by('avg_score')
        # for number, submission in enumerate(submissions, 1):
        #     submission.rank = number
        #     submission.save()

        # messages.success(request, 'Successfully updated poster scores')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):

    change_list_template = 'change_list_variables.html'

    list_display  = ('variable_name', 'variable_value')

    search_fields = ('variable_name', 'variable_value')

    def render_change_form(self, request, context, *args, **kwargs):
        # TODO : change to display on change_list instead
        # here we define a custom template
        self.change_form_template = 'change_form.html'
        help_text = [' Set the following (case sensitive) variables:',
                     'YEAR : The year the retreat',
                     'DATESTRING : the dates of the retreat.',
                     'LOCATION : The location name',
                     """LOCATION_URL : The URL that links to the location webpage.
                                       Start the url with https://
                     """,
                     ]
        # \t example: Thursday, October 6, 2016 and Friday, October 7, 2016
        extra = {
            'has_file_field': True, # Make your form render as multi-part.
            'help_text': help_text
        }
        context.update(extra)
        # superclass = super(ReportOptions, self)
        # return superclass.render_change_form(request, context, *args, **kwargs)
        return super().render_change_form(request, context, *args, **kwargs)

    # TODO : Fix this
    # extra_context = {'help_text': [' Set the following (case sensitive) variables:',
    #                                'YEAR : The year the retreat',
    #                                'DATESTRING : the dates of the retreat.',
    #                                'LOCATION : The location name',
    #                                'LOCATION_URL : The URL that links to the location webpage',]
    # }
    # def changelist_view(self, request, extra_context=None):
    #     print(self.extra_context)
    #     return super(VariableAdmin, self).changelist_view(request, extra_context=self.extra_context)


@admin.register(Submission)
class SubmissionAdmin(MyAdmin):

    change_list_template = 'change_list_submission.html'

    list_display  = ('user', 'presentation', 'title', 'authors', 'PI',
                     'poster_number', 'scores', 'avg_score','rank')

    search_fields = ('user', 'presentation', 'title', 'authors', 'PI', 'poster_number')

    sortable_fields = ('user', 'presentation', 'title', 'PI', 'poster_number', 'avg_score', 'rank')

    ordering = ('avg_score',)

    list_filter = ('user__presentation',  'PI', ('rank',  ValueRangeFilter), 'avg_score')

    # list_select_related = True  # not needed?

    actions = [export_as_csv_action('Download Selected',
                                    fields=list_display,
                                    output_name='BMB_Registrants'),
               ]

    def presentation(self, obj):
        return obj.user.presentation
    presentation.admin_order_field = 'user__presentation'  # allows sorting

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        urls = super().get_urls()
        info = self.opts.app_label, self.opts.model_name

        my_urls = [url(r'assign_poster_numbers/$', wrap(self.assign_poster_numbers),
                       name='{}_{}_assign_poster_numbers'.format(*info)),
                   url(r'submit_scores/$', wrap(self.submit_scores),
                       name='{}_{}_submit_scores'.format(*info)),
                   url(r'calc_poster_scores/$', wrap(self.calc_poster_scores),
                       name='{}_{}_calc_poster_scores'.format(*info)),
        ]

        return my_urls + urls

    def assign_poster_numbers(self, request):
        """
        Assigns poster numbers (overrides/recalculates)
        TODO: Give some notification of success
        """

        users = User.objects.filter(presentation='poster').order_by('last_name')

        if len(users) == 0:
            messages.warning(request, 'No poster submissions present!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        for number, user in enumerate(users, 1):
            try:
                submission = Submission.objects.get(user=user)
            except Exception as e:
                continue

            submission.poster_number = number
            submission.save()

        messages.success(request, 'Successfully updated poster numbers')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def submit_scores(self, request):
        if request.method == 'POST':
            post_data = request.POST
            form      = ScoringForm(post_data)
            form.is_valid()

            max_poster_q = Submission.objects.exclude(poster_number=None).aggregate(models.Max('poster_number'))
            max_poster = max_poster_q.get('poster_number__max', 1)

            cleaned   = form.cleaned_data
            print(cleaned)
            non_null = [x for x in cleaned.values() if x is not None]

            if len(non_null) == 0:
                messages.error(request, 'Not saved, must enter at least 1 poster!')
                return redirect(request.path)
            elif len(set(non_null)) != len(non_null):
                messages.error(request, 'Not saved, cannot enter the same poster more than once')
                return redirect(request.path)
            elif any(x > max_poster for x in non_null):
                invalids = ', '.join([str(x) for x in non_null if x > max_poster])
                messages.error(request, 'Not saved, number(s) {} are not valid posters!'.format(invalids))
                return redirect(request.path)

            for k, v in cleaned:  # keys are ranks (a1, a2, etc..), values are poster numbers
                if v is None:
                    continue

                submission = None
                try:
                    submission = Submission.objects.get(poster_number=int(v))
                except:
                    continue

                scores = submission.scores  # a string of ints, or None
                new_score = k[-1]
                if scores is None:
                    scores = new_score
                    submission.scores = scores
                else:
                    submission.scores += new_score
                submission.save()
            messages.success(request, 'Saved!')
            return redirect(request.path)

        else:
            form = ScoringForm()
            return render(request, 'form.html',
                        {
                            'form': form
                        }
            )

    def calc_poster_scores(self, request):
        """
        Aggregate scores for each poster
        TODO: Give some notification of success
        """
        def maybe_int(x):
            try:
                return int(x)
            except ValueError:
                pass

        submissions = Submission.objects.filter(user__presentation='poster')

        if len(submissions) == 0:
            messages.warning(request, 'No poster submissions present!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        for submission in submissions:
            scores = submission.scores
            tot_scores = len(scores)
            score_sum  = reduce(op.add, filter(None, map(maybe_int, scores)))
            result = score_sum / len(scores)

            submission.avg_score = result
            submission.save()

        # submissions = Submission.objects.exclude(avg_score=None).order_by('avg_score')
        submissions = Submission.objects.filter(user__presentation='poster').order_by('avg_score')
        for number, submission in enumerate(submissions, 1):
            submission.rank = number
            submission.save()

        messages.success(request, 'Successfully updated poster scores')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
