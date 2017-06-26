from django import forms
from django.forms import ModelForm
import datetime
from BMB_Registration.models import *





class LoginForm(forms.Form):

    email    = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class SignupForm(ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label="Confirm Password")
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
