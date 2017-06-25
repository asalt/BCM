#from django.template.loader import get_template
from django.template import Context, RequestContext
#from django.http import HttpResponse, HttpResponseRedirect
# from django.core.context_processors import csrf
from django.shortcuts import render
from BMB_Registration.forms import *
# from orders.models import *
# from django.forms.util import ErrorList
#from django.core.mail import EmailMultiAlternatives
#from django.core.exceptions import ObjectDoesNotExist

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
                                         password=post_data.get('password', '')
                                        )


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

                form.save()

                return render(request, 'data.html',
                              {
                                  'data' : post_data
                              },
                )

            #Need to finish this!!!!!!!!!!!!!!!!!!!!!!!!
            elif post_data.get('password', '') != post_data.get('password2', ''):
                pass

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


