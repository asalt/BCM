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

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display  = ('user', 'title', 'authors', 'PI')

    search_fields = ('user', 'title', 'authors', 'PI')
       
