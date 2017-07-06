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


from BMB_Registration.models import BOOL, GENDER, PRESENTATION, POSITION, TSHIRT_SIZES


from django.forms.utils import ErrorList

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from django import contrib

import datetime
import time
import os
import re

import random

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

        return render(request, 'data.html', )

    else:


        form = LoginForm()

        return render(request, 'form.html', {'form' : form,
                                             'page' : '/login',
                                             'submit_button': 'Log In'
        })


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
                                  'data' : form.cleaned_data,
                                  'submit_button' : 'Update',
                                  'title' : 'Registration' ,
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

                # store user session data and redirect to front page
                request.session['user'] = dict()
                request.session['user']['first_name'] = user.first_name
                request.session['user']['last_name']  = user.last_name
                request.session['user']['email']      = user.email

                return HttpResponseRedirect('/')

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
                         'page' : '/update',
                         'submit_button' : 'Update',
                         'title' : 'Registration' ,
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
                            'data': form.cleaned_data,
                            'title': 'Abstract',
                            'submit_button': 'Save Changes'
                        }
            )

        else:
            return render(request, 'form.html',
                          {'form': form,
                            'title': 'Abstract',
                            'submit_button': 'Save Changes'
                          }
            )

    else:

        form = None

        try:
            form = AbstractForm(instance=Submission.objects.get(user=user))
        except:
            form = AbstractForm()

        return render(request, 'form.html',
                      {'form': form,
                       'title': 'Abstract',
                       'submit_button': 'Submit Abstract'
                      }
        )

def populate_db(request):

    male_first_names  = [
                'JAMES', 'JOHN', 'ROBERT', 'MICHAEL', 'WILLIAM', 'DAVID', 'RICHARD', 'CHARLES',
                'JOSEPH', 'THOMAS', 'CHRISTOPHER', 'DANIEL', 'PAUL', 'MARK', 'DONALD', 'GEORGE',
                'KENNETH', 'STEVEN', 'EDWARD', 'BRIAN', 'RONALD', 'ANTHONY', 'KEVIN', 'JASON',
                'MATTHEW', 'GARY', 'TIMOTHY', 'JOSE', 'LARRY', 'JEFFREY', 'FRANK', 'SCOTT',
                'ERIC', 'STEPHEN', 'ANDREW', 'RAYMOND', 'GREGORY', 'JOSHUA', 'JERRY', 'DENNIS',
                'WALTER', 'PATRICK', 'PETER', 'HAROLD', 'DOUGLAS', 'HENRY', 'CARL', 'ARTHUR',
                'RYAN', 'ROGER',
            ]


    female_first_names = [
                        'MARY',  'PATRICIA',  'LINDA',  'BARBARA',  'ELIZABETH',
                        'JENNIFER',  'MARIA',  'SUSAN',  'MARGARET',  'DOROTHY',
                        'LISA',  'NANCY',  'KAREN',  'BETTY',  'HELEN',  'SANDRA',
                        'DONNA',  'CAROL',  'RUTH',  'SHARON',  'MICHELLE',  'LAURA',
                        'SARAH',  'KIMBERLY',  'DEBORAH',  'JESSICA',  'SHIRLEY',
                        'CYNTHIA',  'ANGELA',  'MELISSA',  'BRENDA',  'AMY',  'ANNA',
                        'REBECCA',  'VIRGINIA',  'KATHLEEN',  'PAMELA',  'MARTHA',
                        'DEBRA',  'AMANDA',  'STEPHANIE',  'CAROLYN',  'CHRISTINE',
                        'MARIE',  'JANET',  'CATHERINE',  'FRANCES',  'ANN',
                        'JOYCE',  'DIANE',
                        ]

    last_names = [
                        'SMITH', 'JOHNSON', 'WILLIAMS', 'BROWN', 'JONES', 'MILLER',
                        'DAVIS', 'GARCIA', 'RODRIGUEZ', 'WILSON', 'MARTINEZ', 'ANDERSON',
                        'TAYLOR', 'THOMAS', 'HERNANDEZ', 'MOORE', 'MARTIN', 'JACKSON',
                        'THOMPSON', 'WHITE', 'LOPEZ', 'LEE', 'GONZALEZ', 'HARRIS', 'CLARK',
                        'LEWIS', 'ROBINSON', 'WALKER', 'PEREZ', 'HALL', 'YOUNG', 'ALLEN',
                        'SANCHEZ', 'WRIGHT', 'KING', 'SCOTT', 'GREEN', 'BAKER', 'ADAMS',
                        'NELSON', 'HILL', 'RAMIREZ', 'CAMPBELL', 'MITCHELL', 'ROBERTS',
                        'CARTER', 'PHILLIPS', 'EVANS', 'TURNER', 'TORRES', 'PARKER',
                        'COLLINS', 'EDWARDS', 'STEWART', 'FLORES', 'MORRIS', 'NGUYEN',
                ]


    title = 'Lorem Ipsum'

    authors = 'X, Y, Z'

    abstract = ('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc elementum lorem ultrices,'
                'convallis massa quis, viverra risus. Curabitur nibh lectus, egestas rhoncus purus nec, '
                'aliquam bibendum mauris. Donec lobortis libero arcu, eu interdum nisl consequat non.'
                ' Cras ante tortor, pharetra sit amet nulla in, lobortis iaculis neque. Aenean urna libero,'
                ' ullamcorper quis libero vitae, euismod mollis leo. Sed eleifend felis non leo aliquet rhoncus.'
                ' Ut ultricies eros id rhoncus facilisis. Nam sit amet ante leo. Pellentesque et euismod quam. '
                'Nullam vulputate justo et tincidunt vehicula. Pellentesque aliquam massa eget orci porta, sed'
                ' vestibulum orci consequat. Aenean ac tellus egestas, pulvinar felis at, tempor nisi. In et '
                'dapibus dui. Quisque suscipit tincidunt suscipit. ')




    for i in range(100):

        gender        = random.choice(GENDER)[0]

        first_name    = random.choice(male_first_names if gender == 'male' else female_first_names)
        last_name     = random.choice(last_names)

        presentation  = random.choice(PRESENTATION)[0]
        position      = random.choice(POSITION)[0]
        tshirt_size   = random.choice(TSHIRT_SIZES)[0]
        stay_at_hotel = random.choice(BOOL)[0]
        share_room    = random.choice(BOOL)[0]
        vegetarian    = random.choice(BOOL)[0]

        department = Department.objects.order_by('?').first()
        lab = PI.objects.order_by('?').first()

        funding_source = '1234567890'

        email = ''.join([chr(x) for x in [random.randint(97, 122) for y in range(15)]])
        email += '@abc.com'

        user = User.objects.create(first_name=first_name, last_name=last_name, gender=gender,
                                   presentation=presentation, position=position, shirt_size=tshirt_size,
                                   funding_source=funding_source, stay_at_hotel=stay_at_hotel,
                                   share_room=share_room, vegetarian=vegetarian, lab=lab,
                                   department=department, email=email)


        if not presentation == 'decline':

            Submission.objects.create(title=title, authors=authors,
                                      abstract=abstract, PI=lab, user=user)

    return render(request, 'data.html')
