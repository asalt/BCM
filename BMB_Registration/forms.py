import datetime

from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Fieldset, Column, Row, Div
from crispy_forms.bootstrap import TabHolder, Tab, InlineRadios


from BMB_Registration.models import *


class ScoringForm(forms.Form):

    a1  = forms.IntegerField(required=False, min_value=1, label='First Rank')
    a2  = forms.IntegerField(required=False, min_value=1, label='Second Rank')
    a3  = forms.IntegerField(required=False, min_value=1, label='Third Rank')
    a4  = forms.IntegerField(required=False, min_value=1, label='Fourth Rank')
    a5  = forms.IntegerField(required=False, min_value=1, label='Fifth Rank')


class LoginForm(forms.Form):

    email    = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


    helper = FormHelper()
    helper.form_id = 'id-loginForm'
    helper.add_input(Submit('submit', 'Login'))
    helper.form_method = 'post'
    helper.form_action = 'login'

    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.layout = Layout(
        'email',
        'password',
        # 'remember_me',
        # StrictButton('Sign in', css_class='btn-default'),
    )



class SignupForm(ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label="Confirm Password")

    helper = FormHelper()
    helper.form_id = 'id-signupForm'
    helper.form_method = 'post'
    helper.form_action = 'signup'
    helper.layout = Layout(
        Div(
            Div('first_name', css_class='col-xs-4'),
            Div('last_name', css_class='col-xs-4'),
            Div('email', css_class='col-xs-4'),
            css_class='row-fluid'),

        Div(
            Div('password', css_class='col-xs-6'),
            Div('password2', css_class='col-xs-6'),
            css_class='row-fluid'),

        Div(
            Div('department', css_class='col-xs-4'),
            Div('lab', css_class='col-xs-4'),
            Div('position', css_class='col-xs-4'),
            css_class='row-fluid'),

        Div(
            # Div('shirt_size', css_class='col-xs-3'),
            Div(InlineRadios('stay_at_hotel'), css_class='col-xs-3'),
            Div(InlineRadios('gender'), css_class='col-xs-3'),
            Div(InlineRadios('vegetarian'), css_class='col-xs-3'),
            Div(InlineRadios('presentation'), css_class='col-xs-3'),
            css_class='row-fluid'),

        Div(
            Div(Field('shirt_size'), css_class='col-xs-3'),
            Div(Field('roommate_pref'), css_class='col-xs-9'),
            css_class='row-fluid'),

        Div(Div('funding_source', css_class='col-xs-12'), css_class='row-fluid'),

    )
    helper.add_input(Submit('update', 'Register'))


    class Meta:

        model = User

        fields = ('first_name',
                  'last_name',
                  'gender',
                  'lab',
                  'department',
                  'position',
                  'password',
                  'password2',
                  'email',
                  'shirt_size',
                  'stay_at_hotel',
                  'presentation',
                  'vegetarian',
                  'roommate_pref',
                  'funding_source',
        )

        widgets = {
            'password': forms.PasswordInput(),
        }



    def clean_first_name(self):

        return self.cleaned_data['first_name'].strip().capitalize()

    def clean_last_name(self):

        return self.cleaned_data['last_name'].strip().capitalize()



class UpdateForm(ModelForm):

    helper = FormHelper()
    helper.form_id = 'id-updateForm'
    helper.form_method = 'post'
    helper.form_action = 'update'
    # helper.help_text_inline = True
    helper.layout = Layout(
        Div(
            Div('first_name', css_class='col-xs-4'),
            Div('last_name', css_class='col-xs-4'),
            Div('email', css_class='col-xs-4'),
            css_class='row-fluid'),

        Div(
            Div('department', css_class='col-xs-4'),
            Div('lab', css_class='col-xs-4'),
            Div('position', css_class='col-xs-4'),
            css_class='row-fluid'),

        Div(
            # Div('shirt_size', css_class='col-xs-3'),
            Div(InlineRadios('stay_at_hotel'), css_class='col-xs-3'),
            Div(InlineRadios('gender'), css_class='col-xs-3'),
            Div(InlineRadios('vegetarian'), css_class='col-xs-3'),
            Div(InlineRadios('presentation'), css_class='col-xs-3'),
            css_class='row-fluid'),

        Div(
            Div(Field('shirt_size'), css_class='col-xs-3'),
            Div(Field('roommate_pref'), css_class='col-xs-9'),
            css_class='row-fluid'),

        Div(Div('funding_source', css_class='col-xs-12'), css_class='row-fluid'),

    )
    helper.add_input(Submit('update', 'Update'))

    class Meta:

        model = User

        fields = ('first_name',
                  'last_name',
                  'gender',
                  'lab',
                  'department',
                  'position',
                  'email',
                  'shirt_size',
                  'stay_at_hotel',
                  'presentation',
                  'vegetarian',
                  'roommate_pref',
                  'funding_source',
        )


    def clean_first_name(self):

        return self.cleaned_data['first_name'].strip().capitalize()

    def clean_last_name(self):

        return self.cleaned_data['last_name'].strip().capitalize()


class AbstractForm(ModelForm):


    class Meta:
        model = Submission
        fields = ('title',
                  'authors',
                  'abstract',
        )
