import csv
#from django.template.loader import get_template
from django.template import Context, RequestContext
#from django.http import HttpResponse, HttpResponseRedirect
# from django.core.context_processors import csrf
from django.shortcuts import render, redirect
from BMB_Registration.forms import *
# from django.forms.util import ErrorList
#from django.core.mail import EmailMultiAlternatives
#from django.core.exceptions import ObjectDoesNotExist
from BMB_Registration.models import User
from BMB_Registration.models import Submission

from django.forms.utils import ErrorList

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from django import contrib

import datetime
import time
import os
import re

#def login_required(func):
#

#    user = request.session.get('user')

#    if user is None:


#        def inner(*args, **kwargs):
#            return func(*args, **kwargs)
#        return inner

def is_authenticated(request):

    if request.session.get('user') is not None:
        return True

    else:
        return False



def home(request):

    if is_authenticated(request):

        return render(request, 'data.html', {'data' : request.session['user']})

    else:


        form = LoginForm()

        return render(request, 'form.html', {'form' : form,
                                             'page' : '/login'})


def login(request):

    if request.method == 'POST':

        post_data     = request.POST
        form          = LoginForm(post_data)
        user          = None



        if form.is_valid():

            email     = post_data['email']
            password  = post_data['password']

            try:
                user = User.objects.get(
                                         email=post_data.get('email', ''),
                                         # password=post_data.get('password', '')
                                        )
                if not user.check_password(password):
                    message = 'The password is incorrect.'
                    # messages.error(request, message)
                    form.errors['password'] = ErrorList([message])

                    return render(request, 'form.html', {'form' : form})



                request.session['user'] = dict()
                request.session['user']['first_name'] = user.first_name
                request.session['user']['last_name']  = user.last_name
                request.session['user']['email']      = user.email


                return HttpResponseRedirect('/')


            except User.DoesNotExist:

                try:
                    user = User.objects.get(
                                            email=post_data.get('email', ''),
                                            )

                    message = 'The password is incorrect.'
                    # messages.error(request, message)
                    form.errors['password'] = ErrorList([message])

                    return render(request, 'form.html', {'form' : form})


                except User.DoesNotExist:

                    message = ('This email address has not registered.'
                                'You\'ll need to sign up.')

                    # messages.error(request, message)
                    form.errors['email'] = ErrorList([message])

                    return render(request, 'form.html', {'form' : form})

    else:

        return HttpResponseRedirect('/')


def logout(request):

    try:
        request.session.flush()
    except:
        pass

    return HttpResponseRedirect('/')


def signup(request):

    #if form has been submitted
    if request.method == 'POST':

        post_data = request.POST

        #if user is logged in, process as UpdateForm
        if is_authenticated(request):


            email = request.session['user'].get('email')
            form  = UpdateForm(post_data, instance=User.objects.get(email=email))

            if form.is_valid():

                form.save()

                return render(request, 'data.html',
                              {
                                  'data' : form.cleaned_data
                              },
                )

            else:

                return render(request, 'form.html',
                              {
                                  'form' : form
                              },
                )

        #if user is not logged in, process as SignupForm
        else:

            form = SignupForm(post_data)


            if post_data.get('password', '') == post_data.get('password2', '') \
               and form.is_valid() :
                user = form.save(commit=False)
                password = form.cleaned_data['password']
                user.set_password(password)
                user.save()

                return render(request, 'data.html',
                              {
                                  'data' : post_data
                              },
                )

            elif post_data.get('password', '') != post_data.get('password2', ''):
                message = 'Passwords do not match!'
                form.errors['password2'] = ErrorList([message])
                return render(request, 'form.html', {'form' : form})

            else:
                return render(request, 'form.html',
                              {
                                  'form' : form
                              },
                )

    #if form hasn't been submitted, determine appropriate form
    else:
        form = None

        try:

            email = request.session['user']['email']

            form  = UpdateForm(instance=User.objects.get(email=email))


            return render(request, 'form.html',
                        {'form' : form,
                         'page' : '/update'
                        },
            )


        except Exception as e:

            print(e)
            form  = SignupForm()

            return render(request, 'form.html',
                            {'form' : form,
                            #'message' : 'Signup',
                            'page' : '/signup'
                            },
            )

def abstract_submission(request):

    email = request.session['user']['email']
    user  = User.objects.get(email=email)

    if request.method == 'POST':

        post_data = request.POST
        instance  = Submission.objects.get_or_create(user=user, PI=user.lab)[0]
        form      = AbstractForm(post_data, instance=instance)

        if form.is_valid():

            Submission.objects.filter(user=user).update(**form.cleaned_data)


            return render(request, 'data.html',
                        {
                        'page': '/',
                        'data': form.cleaned_data
                        }
            )

        else:
            return render(request, 'form.html',
                          {'form': form}
            )

    else:

        form = None

        try:
            form = AbstractForm(instance=Submission.objects.get(user=user))
        except:
            form = AbstractForm()

        return render(request, 'form.html',
                      {'form': form}
        )

def score_submission(request):


    if request.method == 'POST':
        post_data = request.POST
        form      = ScoringForm(post_data)
        form.is_valid()
        cleaned   = form.cleaned_data

        for k, v in form.cleaned_data.items():  # keys are ranks (a1, a2, etc..), values are poster numbers
            if v is None:
                continue

            submission = None

            try:
                submission = Submission.objects.get(poster_number=int(v))
            except:
                continue

            scores = submission.scores
            new_score = k[-1]

            if scores is None:
                scores = new_score

                submission.scores = scores

            else:
                submission.scores += new_score

            submission.save()

        return redirect(request.path)

    else:
        form = ScoringForm()
        return render(request, 'form.html',
                      {
                          'form': form
                      }
        )


def assign_poster_numbers(request):
    """
    only for admin
    """

    # def inner(modeladmin, request, queryset):
    users = User.objects.filter(presentation='poster').order_by('last_name')
    for number, user in enumerate(users, 1):
        try:
            submission = Submission.objects.get(user=user)
        except Exception as e:
            continue

        submission.poster_number = number
        submission.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def export_as_csv(request,  description="Export selected objects as CSV file",
                  output_name='download',
                  fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    TABLES = {'Submissions': Submission,
              'Users': User}


    table_name = os.path.split(request.path)[-1]
    table = TABLES.get(table_name)
    if table is None:
        #TODO : Warn invalid?
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if not fields:
        field_names = table.list_display
    else:
        field_names = fields

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=BMB_Retreat_{}.csv'.format(table_name)
    writer = csv.writer(response)
    if header:
        writer.writerow(field_names)
    for entry in table.objects.all():
        row = [getattr(entry, field)() if callable(getattr(entry, field)) else getattr(entry, field) for field in field_names]
        writer.writerow(row)
    return response
