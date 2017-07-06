import datetime

from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Fieldset, Column, Row, Div, ButtonHolder, Button, HTML
from crispy_forms.bootstrap import TabHolder, Tab, InlineRadios, FormActions


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
    # helper.add_input(Submit('submit', 'Login'))
    helper.form_method = 'post'
    helper.form_action = 'login'

    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.layout = Layout(
        Div(
            'email',
            'password',
            FormActions(
                ButtonHolder(Submit('submit', 'Login'),
                             HTML("""
                             <a href="/password_reset" style="color: #000000">
                             <input type="button" class="btn" value="Reset Password">
                             </a>
                             """)

                ),
            ),
            css_class='col-lg-12'
            )
        # 'remember_me',
        # StrictButton('Sign in', css_class='btn-default'),
    )

class ResetPasswordForm(forms.Form):

    email    = forms.EmailField()

    helper = FormHelper()
    helper.form_id = 'id-Form'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-10'
    helper.form_method = 'post'
    helper.form_action = 'password_reset'
    helper.layout = Layout('email',
                           helper.add_input(Submit('password_reset', 'Reset Password'))
    )

class ChangePasswordForm(forms.Form):

    old_password = forms.CharField(widget=forms.PasswordInput,
                                   label="Old Password")
    password = forms.CharField(widget=forms.PasswordInput,
                               label="New Password")
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label="Confirm New Password")

    helper = FormHelper()
    helper.form_id = 'id-passwordForm'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-10'
    helper.form_method = 'post'
    helper.form_action = 'change_password'
    helper.layout = Layout('old_password',
                           'password',
                           'password2',
                           helper.add_input(Submit('change_password', 'Update Password'))
    )


class NewPasswordForm(forms.Form):

    password = forms.CharField(widget=forms.PasswordInput,
                               label="New Password")
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label="Confirm New Password")

    helper = FormHelper()
    helper.form_id = 'id-passwordForm'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-10'
    helper.form_method = 'post'
    helper.form_action = 'change_password'
    helper.layout = Layout('password',
                           'password2',
                           helper.add_input(Submit('change_password', 'Update Password'))
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
            css_class='row'),

        Div(
            Div('password', css_class='col-xs-6'),
            Div('password2', css_class='col-xs-6'),
            css_class='row'),

        Div(
            Div('department', css_class='col-xs-4'),
            Div('lab', css_class='col-xs-4'),
            Div('position', css_class='col-xs-4'),
            css_class='row'),

        Div(
            Div('shirt_size', css_class='col-xs-3'),
            Div(InlineRadios('stay_at_hotel'), css_class='col-xs-2'),
            Div(InlineRadios('gender'), css_class='col-xs-2'),
            Div(InlineRadios('vegetarian'), css_class='col-xs-2'),
            Div(InlineRadios('presentation'), css_class='col-xs-3'),
            css_class='row'),

        Div(
            Div(Field('roommate_pref'), css_class='col-xs-6 col-xs-offset-3'),
            css_class='row'),

        Div(Div('funding_source', css_class='col-xs-12'), css_class='row'),

    )
    Div(Div(helper.add_input(Submit('update', 'Register')), css_class='col-md-12'), css_class='row')


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
            css_class='row'),

        Div(
            Div('department', css_class='col-xs-4'),
            Div('lab', css_class='col-xs-4'),
            Div('position', css_class='col-xs-4'),
            css_class='row'),

        Div(
            Div('shirt_size', css_class='col-xs-3'),
            Div(InlineRadios('stay_at_hotel'), css_class='col-xs-3'),
            Div(InlineRadios('gender'), css_class='col-xs-3'),
            Div(InlineRadios('vegetarian'), css_class='col-xs-3'),
            Div(InlineRadios('presentation'), css_class='col-xs-3'),
            css_class='row'),

        Div(
            Div(Field('roommate_pref'), css_class='col-xs-12'),
            css_class='row'),

        Div(Div('funding_source', css_class='col-xs-12'), css_class='row'),

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

    # abstract = forms.CharField(widget=forms.Textarea)

    helper = FormHelper()
    helper.form_id = 'id-abstractForm'
    helper.form_method = 'post'
    helper.form_action = 'abstract'
    helper.add_input(Submit('update', 'Save Changes'))

    class Meta:
        model = Submission
        fields = ('title',
                  'authors',
                  'abstract',
        )
