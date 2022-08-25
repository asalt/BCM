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

# from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.conf.urls import url
from django.contrib import messages
from django.contrib.admin import DateFieldListFilter
from django.core.files.storage import FileSystemStorage
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.core.exceptions import ObjectDoesNotExist

from django.core.mail import send_mail
from django.template import loader

from BMB_Registration.models import *
from BMB_Registration.actions import *
from BMB_Registration.forms import *
from BMB_Registration.valuerangefilter import ValueRangeFilter
from BMB_Registration import poster_matching
from BMB_Registration.poster_matching import AssignmentError

from BCM.settings import DEFAULT_FROM_EMAIL

JUDGE_SEP = " | "

admin.site.site_header = "BMB Retreat Admin"

# class IntFieldListFilter(FieldListFilter):
#     def __init__(self, field, request, params, model, model_admin, field_path):
#         "docstring"


class MyAdmin(admin.ModelAdmin):

    change_list_template = None  # change as desired
    list_display = None
    export_header = True
    export_fields = None  # will use list_display if unchanged

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        urls = super().get_urls()

        info = self.opts.app_label, self.opts.model_name

        my_urls = [
            url(
                r"export_as_csv/$",
                wrap(self.export_as_csv),
                name="{}_{}_export_as_csv".format(*info),
            )
        ]

        return my_urls + urls

    def export_as_csv(self, request):
        """
        This function returns an export csv action
        'fields' and 'exclude' work like in django ModelForm
        'header' is whether or not to output the column names as the first row
        """
        table = self.model
        # table_name = table.db_table
        table_name = self.opts.model_name

        if table is None:
            # TODO : Warn invalid?
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        if self.export_fields is not None:
            field_names = self.export_fields
        elif self.list_display is None:
            field_names = [field.name for field in self.opts.fields]
        else:
            field_names = self.list_display

        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = "attachment; filename=BMB_Retreat_{}.csv".format(table_name)
        writer = csv.writer(response)
        if self.export_header:
            writer.writerow(field_names)
        for entry in table.objects.all():
            row = [
                getattr(entry, field)()
                if callable(getattr(entry, field))
                else getattr(entry, field)
                for field in field_names
            ]
            writer.writerow(row)
        return response


class BulkAdmin(admin.ModelAdmin):

    change_list_template = "change_list_bulk.html"  # change as desired
    list_display = None
    entry_name = "DEFAULT"
    help_text = None

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        urls = super().get_urls()

        info = self.opts.app_label, self.opts.model_name

        my_urls = [
            url(r"bulk_add/$", wrap(self.bulk_add), name="{}_{}_bulk_add".format(*info))
        ]

        return my_urls + urls

    def bulk_add(self, request):
        """ """
        if request.method == "POST":

            myfile = request.FILES.get("myfile")

            if myfile is None:
                messages.warning(request, "Must select a file for upload first!")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

            fs = FileSystemStorage(location=gettempdir())
            filename = fs.save(myfile.name, myfile)
            fullname = fs.path(filename)
            if not os.path.exists(fullname):
                messages.error(request, "Internal server error accessing file.")
            uploaded_file_url = fs.url(filename)
            entries = self.parse_file(fullname)
            num_saved = self.save_results(entries)

            fs.delete(filename)

            path = Path(request.path)
            redirection = path.parents[0].as_posix()  # go up 1

            if num_saved > 0:
                if num_saved > 1:
                    msg_str = "Successfully uploaded {} {}".format(
                        num_saved, self.model._meta.verbose_name_plural
                    )
                else:
                    msg_str = "Successfully uploaded {} {}".format(
                        num_saved, self.model._meta.verbose_name
                    )
                messages.success(request, msg_str)
            elif num_saved == 0:
                messages.warning(
                    request,
                    """Failed to upload any {},
                                 has this file already been uploaded?""".format(
                        self.model._meta.verbose_name_plural
                    ),
                )
            return HttpResponseRedirect(redirection)

        return render(
            request,
            "simple_upload.html",
            context={
                "entry_name": self.entry_name,
                "additional_help": self.help_text,
            },
        )

    def parse_file(self, filename):
        entries = list()
        with open(filename, "r") as f:
            for line in f:
                entries.append(line)
        return entries

    def save_results(self, entries):
        raise NotImplementedError("Must subclass and implement")


@admin.register(PI)
class PIAdmin(BulkAdmin):

    entry_name = "PI"
    help_text = (
        'Each PI entry should be of form <font color="red">LastName, FirstName</font>'
    )

    list_display = ("last_name", "first_name")

    search_fields = ("last_name", "first_name")

    def save_results(self, entries):

        counter = 0

        for entry in entries:
            print(entry, len(entry))

            if len(entry.strip()) == 0:
                continue

            split = entry.strip().split(",")

            if len(split) == 1:  # invalid format, store all in lastname
                last = split[0].strip()
                first = ""
            elif len(split) >= 2:  # expected format
                last = split[0].strip()
                first = split[1].strip()

            q = PI.objects.filter(last_name=last, first_name=first)
            if len(q) != 0:  # already exists
                continue

            PI.objects.create(last_name=last, first_name=first)
            counter += 1

        return counter


@admin.register(Department)
class DepartmentAdmin(BulkAdmin):

    entry_name = "Department"

    list_display = ("name",)

    search_fields = ("name",)

    def save_results(self, entries):

        counter = 0

        for entry in entries:

            q = Department.objects.filter(name=entry)
            if len(q) != 0:  # already exists
                continue

            Department.objects.create(name=entry)
            counter += 1

        return counter


@admin.register(User)
class UserAdmin(MyAdmin):

    list_per_page = 15

    change_list_template = "change_list_user.html"
    # change_list_template = 'change_list_ext.html'

    list_display = (
        "last_name",
        "first_name",
        "date_registered",
        "gender",
        "department",
        "lab",
        "position",
        "email",
        "date_registered",
        "shirt_size",
        "presentation",
        "funding_source",
        "stay_at_hotel",
        "share_room",
        "roommate_pref",
        "vegetarian",
        "rank_posters",
        "detailed_posters",
    )

    search_fields = (
        "last_name",
        "first_name",
        "gender",
        "department__name",
        "lab__last_name",
        "lab__first_name",
        "position",
        "email",
        "date_registered",
        "shirt_size",
        "presentation",
        "funding_source",
        "stay_at_hotel",
        "share_room",
        "roommate_pref",
        "vegetarian",
    )

    exclude = ("password",)  # do not let admin see/edit the (encrypted) password

    actions = [
        export_as_csv_action(
            "Download Selected", fields=list_display, output_name="BMB_Registrants"
        )
    ]

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        urls = super().get_urls()
        info = self.opts.app_label, self.opts.model_name

        my_urls = [
            url(
                r"assign_judges/$",
                wrap(self.assign_judges),
                name="{}_{}_assign_judges".format(*info),
            ),
            url(
                r"remind_users/$",
                wrap(self.remind_users),
                name="{}_{}_remind_users".format(*info),
            ),
        ]

        return my_urls + urls

    def assign_judges(self, request):
        """ """
        # days = ["monday", "tusday", "wednesday", "thursday", "friday",
        #         "saturday", "sunday"]

        restriction_lookup = {"both": None, "thursday": 1, "friday": 2}
        users = list()
        for user in User.objects.all():

            attendance = user.attendance
            restriction = restriction_lookup.get(attendance.lower(), None)

            d = {
                "identifier": user.email,
                "lab": user.lab,
                "poster_number": None,
                "restriction": restriction,
            }

            if user.presentation == "poster":
                try:
                    q = Submission.objects.get(user=user)
                    d["poster_number"] = q.poster_number
                except ObjectDoesNotExist:
                    # continue
                    pass

            users.append(d)
        print("Assigning posters for", len(users), "judges")

        if len(users) == 0:
            messages.error(request, "No users!")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        elif len([user for user in users if user["poster_number"] is not None]) == 0:

            messages.warning(
                request,
                """Poster number are not assigned
            or no users have submitted abstracts yet!
            """,
            )
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        try:
            judges, presenters = poster_matching.main(users)
        except AssignmentError as e:
            # messages.error(request, e)
            messages.warning(request, e)
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        print(len(judges))
        for judge in judges:
            email = judge.identifier
            to_rank = JUDGE_SEP.join(map(str, sorted(judge.posters)))
            to_detail = JUDGE_SEP.join(map(str, sorted(judge.detailed_posters)))
            print((email, to_rank, to_detail))
            user = User.objects.get(email=email)
            user.rank_posters = to_rank
            user.detailed_posters = to_detail
            user.save()

        for presenter in presenters:
            email = presenter.identifier
            q = Submission.objects.get(user__email=email)
            to_rank = JUDGE_SEP.join(map(str, sorted(presenter.posters)))
            to_detail = JUDGE_SEP.join(map(str, sorted(presenter.detailed_posters)))
            q.rank_judges = to_rank
            q.detailed_judges = to_detail
            q.assigned_ranks = len(presenter.posters)
            q.assigned_detailed = len(presenter.detailed_posters)
            q.save()

        messages.success(request, "Successfully assigned judges to posters")

        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    def remind_users(self, request):

        poster_users = User.objects.filter(presentation="poster")
        sub_posters = Submission.objects.filter(user__presentation="poster")
        sub_emails = {x.user.email for x in sub_posters}
        poster_useremails = {x.email for x in poster_users}

        to_alert = poster_useremails - sub_emails

        if len(to_alert) == 0:
            messages.success(
                request,
                "All poster presenters have submitted abstracts! No email being sent.",
            )
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        else:

            site_name = "BMB Retreat Registration"
            domain = request.get_host()
            email_template_name = "submit_abstract_email_reminder.html"
            use_https = False
            for email in to_alert:
                user = User.objects.get(email=email)

                c = {
                    "site_name": site_name,
                    "user": user,
                    "protocol": use_https and "https" or "http",
                    "domain": domain,
                }
                send_mail(
                    subject="BMB Retreat Registration Abstract Submission Requirement",
                    message=loader.render_to_string(email_template_name, c),
                    from_email=DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )

            messages.success(
                request, "Sent reminder emails to {} user(s)".format(len(to_alert))
            )
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):

    change_list_template = "change_list_variables.html"

    list_display = ("variable_name", "variable_value")

    search_fields = ("variable_name", "variable_value")

    def render_change_form(self, request, context, *args, **kwargs):
        # TODO : change to display on change_list instead
        # here we define a custom template
        self.change_form_template = "change_form.html"
        help_text = [
            " Set the following (case sensitive) variables:",
            "YEAR : The year the retreat",
            "DATESTRING : the dates of the retreat.",
            "LOCATION : The location name",
            """LOCATION_URL : The URL that links to the location webpage.
                                       Start the url with https://
                     """,
        ]
        # \t example: Thursday, October 6, 2016 and Friday, October 7, 2016
        extra = {
            "has_file_field": True,  # Make your form render as multi-part.
            "help_text": help_text,
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

    list_per_page = 20

    change_list_template = "change_list_submission.html"

    list_display = (
        "user",
        "presentation",
        "title",
        "presenter",
        "authors",
        "final_author",
        "PI",
        "poster_number",
        "avg_score",
        "rank",
        "assigned_ranks",
        "assigned_detailed",
    )

    # export_fields = (*list_display, 'abstract')
    export_fields = tuple(list(list_display) + ["abstract"])

    search_fields = (
        "user__last_name",
        "user__first_name",
        "user__presentation",
        "title",
        "authors",
        "PI__last_name",
        "poster_number",
    )

    sortable_fields = (
        "user",
        "presentation",
        "title",
        "PI",
        "poster_number",
        "avg_score",
        "rank",
        "assigned_ranks",
        "assigned_detailed",
    )

    ordering = ("avg_score",)

    list_filter = ("user__presentation", "PI", ("rank", ValueRangeFilter), "avg_score")

    # list_select_related = True  # not needed?

    actions = [
        export_as_csv_action(
            "Download Selected", fields=list_display, output_name="BMB_Registrants"
        ),
    ]

    def presentation(self, obj):
        return obj.user.presentation

    presentation.admin_order_field = "user__presentation"  # allows sorting

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        urls = super().get_urls()
        info = self.opts.app_label, self.opts.model_name

        my_urls = [
            url(
                r"assign_poster_numbers/$",
                wrap(self.assign_poster_numbers),
                name="{}_{}_assign_poster_numbers".format(*info),
            ),
            url(
                r"submit_scores/$",
                wrap(self.submit_scores),
                name="{}_{}_submit_scores".format(*info),
            ),
            url(
                r"calc_poster_scores/$",
                wrap(self.calc_poster_scores),
                name="{}_{}_calc_poster_scores".format(*info),
            ),
        ]

        return my_urls + urls

    def assign_poster_numbers(self, request):
        """
        Assigns poster numbers (overrides/recalculates)
        TODO: Give some notification of success
        """

        submissions = Submission.objects.filter(user__presentation="poster").order_by(
            "user__last_name"
        )

        all_submissions = Submission.objects.all()
        all_submissions.update(poster_number=None)
        for s in all_submissions:
            s.save()

        if len(submissions) == 0:
            messages.warning(request, "No poster submissions present!")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        for number, submission in enumerate(submissions, 1):

            print(number, submission, submission.poster_number)
            submission.poster_number = number
            submission.save()

        messages.success(request, "Successfully updated poster numbers")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    def submit_scores(self, request):

        if request.method == "POST":
            post_data = request.POST
            form = ScoringForm(post_data)
            form.is_valid()

            max_poster_q = Submission.objects.exclude(poster_number=None).aggregate(
                models.Max("poster_number")
            )
            max_poster = max_poster_q.get("poster_number__max", 1)

            cleaned = form.cleaned_data
            non_null = [x for x in cleaned.values() if x is not None]

            if len(non_null) == 0:
                messages.warning(request, "Not saved, must enter at least 1 poster!")
                return redirect(request.path)

            elif len(set(non_null)) != len(non_null):
                messages.warning(
                    request, "Not saved, cannot enter the same poster more than once"
                )
                return redirect(request.path)

            elif any(x > max_poster for x in non_null):
                invalids = ", ".join([str(x) for x in non_null if x > max_poster])
                messages.warning(
                    request,
                    "Not saved, number(s) {} are not valid posters!".format(invalids),
                )
                return redirect(request.path)

            scores = dict()  # poster_number -> rank
            for (
                k,
                v,
            ) in (
                cleaned.items()
            ):  # keys are ranks (a1, a2, etc..), values are poster numbers

                rank = k[1:]
                scores[v] = rank

            max_set = PosterRank.objects.aggregate(models.Max("rank_set")).get(
                "rank_set__max"
            )
            if max_set is None:
                max_set = 0
            print(max_set)
            for poster_number, rank in scores.items():
                submission = Submission.objects.get(poster_number=poster_number)
                if submission is None:
                    continue  # we check for this up above
                poster_rank = PosterRank(
                    rank_set=max_set + 1, rank=rank, poster_number=submission
                )
                poster_rank.save()

            messages.success(request, "Saved!")
            return redirect(request.path)

        else:
            form = ScoringForm()

            path = Path(request.path)
            previous = path.parents[0].as_posix()  # go up 1

            return render(
                request,
                "admin_form.html",
                {
                    "form": form,
                    "opts": self.opts,
                    "previous": previous,
                },
            )

            # return render(request, '/admin/poster_score_form.html',
            #             {
            #                 'form': form
            #             }
            # )

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

        submissions = Submission.objects.filter(user__presentation="poster")

        if len(submissions) == 0:
            messages.warning(request, "No poster submissions present!")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        for submission in submissions:
            # here could implement different logic
            # this is just an average

            poster_ranks = PosterRank.objects.filter(poster_number=submission)
            scores = [x.rank for x in poster_ranks]
            print(submission, scores)
            if not scores:
                continue
            tot_scores = len(scores)
            score_sum = reduce(op.add, filter(None, map(maybe_int, scores)))
            print(submission, score_sum)

            result = score_sum / len(scores)
            submission.avg_score = result
            submission.save()

        # submissions = Submission.objects.exclude(avg_score=None).order_by('avg_score')
        submissions = (
            Submission.objects.exclude(avg_score=None)
            .filter(user__presentation="poster")
            .order_by("avg_score")
        )
        for number, submission in enumerate(submissions, 1):
            submission.rank = number
            submission.save()

        messages.success(request, "Successfully updated poster scores")

        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@admin.register(PosterRank)
class PosterRankAdmin(MyAdmin):

    change_list_template = "change_list_ext.html"
    list_per_page = 20
    list_display = ("rank_set", "rank", "poster_number")


@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    # list_display = ('file_link',)

    pass

    # change_list_template = 'change_list_ext.html'
    # list_per_page = 20
    # list_display = ('rank_set', 'rank', 'poster_number')
