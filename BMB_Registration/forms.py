import datetime

from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Fieldset, Column, Row, Div, ButtonHolder, Button, HTML
from crispy_forms.bootstrap import TabHolder, Tab, InlineRadios, FormActions
from captcha.fields import CaptchaField


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

                             <a href="/signup">
                             <input type="button" class="btn btn-success" value="Sign Up">
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
    captcha  = CaptchaField(generator='captcha.helpers.math_challenge')

    helper = FormHelper()
    helper.form_id = 'id-Form'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-10'
    helper.form_method = 'post'
    helper.form_action = 'password_reset'
    helper.layout = Layout('email',
                           'captcha',
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
    captcha = CaptchaField(generator='captcha.helpers.math_challenge')

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
            Div('lab_dept', css_class='col-xs-4'),
            Div('position', css_class='col-xs-4'),
            css_class='row'),

        Div(
            Div(InlineRadios('gender'), css_class='col-xs-4'),
            Div(InlineRadios('vegetarian'), css_class='col-xs-4'),
            Div(InlineRadios('presentation'), css_class='col-xs-4'),
            css_class='row'),

        Div(
            Div('shirt_size', css_class='col-xs-4'),
            Div(InlineRadios('stay_at_hotel'), css_class='col-xs-4'),
            Div('attendance', css_class='col-xs-4'),
            css_class='row'),

        # Div(
        #     Div('shirt_size', css_class='col-xs-3'),
        #     Div(InlineRadios('stay_at_hotel'), css_class='col-xs-2'),
        #     Div(InlineRadios('gender'), css_class='col-xs-2'),
        #     Div(InlineRadios('vegetarian'), css_class='col-xs-2'),
        #     Div(InlineRadios('presentation'), css_class='col-xs-3'),
        #     css_class='row'),

        Div(
            Div(Field('roommate_pref'), css_class='col-xs-6 col-xs-offset-3'),
            css_class='row'),

        Div(Div('funding_source', css_class='col-xs-12'), css_class='row'),
        Field('captcha')

    )
    Div(Div(helper.add_input(Submit('update', 'Register')), css_class='col-md-6'), css_class='row')


    class Meta:

        model = User

        fields = ('first_name',
                  'last_name',
                  'gender',
                  'lab',
                  'department',
                  'lab_dept',
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
                  'attendance',
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
            Div('first_name', css_class='col-xs-6'),
            Div('last_name', css_class='col-xs-6'),
            # Div('email', css_class='col-xs-4'),  # don't let users change their email
            css_class='row'),

        Div(
            Div('department', css_class='col-xs-4'),
            Div('lab', css_class='col-xs-4'),
            Div('lab_department', css_class='col-xs-4'),
            Div('position', css_class='col-xs-4'),
            css_class='row'),

        Div(
            Div(InlineRadios('gender'), css_class='col-xs-4'),
            Div(InlineRadios('vegetarian'), css_class='col-xs-4'),
            Div(InlineRadios('presentation'), css_class='col-xs-4'),
            css_class='row'),

        Div(
            Div('shirt_size', css_class='col-xs-4'),
            Div(InlineRadios('stay_at_hotel'), css_class='col-xs-4'),
            Div('attendance', css_class='col-xs-4'),
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
                  'lab_dept',
                  'position',
                  'shirt_size',
                  'stay_at_hotel',
                  'presentation',
                  'vegetarian',
                  'roommate_pref',
                  'funding_source',
                  'attendance',
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
                  'presenter',
                  'authors',
                  'final_author',
                  'abstract',
        )


class UploadForm(ModelForm):

    helper = FormHelper()

    helper.form_id = 'id-uploadForm'
    helper.form_method = 'post'
    helper.form_action = 'upload'

    helper.add_input(Submit('submit', 'Upload'))

    class Meta:
        model = Upload
        fields = ('upload',)


    CONTENT_TYPES = ['txt']
    MAX_UPLOAD_SIZE = "20971520"

#     def is_valid(self):

#         ModelForm.is_valid(self)

#         # content = self.cleaned_data['upload']
#         print(dir(self))
#         print(self.data)
#         content = self.data
#         print(dir(content))
#         print(content)

#         content_type = content.content_type.split('/')[0]

#         if content_type is not None and content_type not in self.CONTENT_TYPES:
#             raise forms.ValidationError(_('File type is not supported'))

#         if content._size > settings.MAX_UPLOAD_SIZE:
#             raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(self.MAX_UPLOAD_SIZE), filesizeformat(content._size)))

#         return content


# class RestrictedFileField(forms.FileField):

#     CONTENT_TYPES = ['txt']
#     MAX_UPLOAD_SIZE = "20971520"
#     def clean_content(self):

#         content = self.cleaned_data['upload']
#         content_type = content.content_type.split('/')[0]

#         if content_type is not None and content_type not in settings.CONTENT_TYPES:
#             raise forms.ValidationError(_('File type is not supported'))

#         if content._size > settings.MAX_UPLOAD_SIZE:
#             raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content._size)))

#         return content
