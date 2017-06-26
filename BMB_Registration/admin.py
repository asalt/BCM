from django.contrib import admin
from BMB_Registration.models import *

# Register your models here.

@admin.register(PI)
class PIAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')

    search_fields = ('last_name', 'first_name')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)

    search_fields = ('name',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

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

@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):

    list_display  = ('variable_name', 'variable_value')

    search_fields = ('variable_name', 'variable_value')

    def render_change_form(self, request, context, *args, **kwargs):
        # here we define a custom template
        self.change_form_template = 'change_form.html'
        help_text = [' Set the following (case sensitive) variables:',
                     'YEAR : The year the retreat',
                     'DATESTRING : the dates of the retreat.',
                     'LOCATION : The location name',
                     'LOCATION_URL : The URL that links to the location webpage',
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

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display  = ('user', 'title', 'authors', 'PI')

    search_fields = ('user', 'title', 'authors', 'PI')
