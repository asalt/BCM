import logging
log = logging.getLogger(__name__)

import csv
import datetime
import time
import os
import re
import base64
from collections import OrderedDict
import mimetypes

import random

#from django.template.loader import get_template
from django.template import Context, RequestContext
#from django.http import HttpResponse, HttpResponseRedirect
# from django.core.context_processors import csrf
from django.shortcuts import render, redirect
# from django.contrib.sites.models import Site
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import send_mail
from django.template import loader
from django.utils.http import int_to_base36, base36_to_int
from django.utils.encoding import force_text
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

from BMB_Registration.forms import *
# from django.forms.util import ErrorList
#from django.core.mail import EmailMultiAlternatives
#from django.core.exceptions import ObjectDoesNotExist
from BMB_Registration.models import User
from BMB_Registration.models import Submission
from BMB_Registration.models import user_directory_path
from BCM.settings import DEFAULT_FROM_EMAIL
from BCM.settings import MEDIA_ROOT
from BCM.settings import AUTH_PASSWORD_VALIDATORS
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth.password_validation import validate_password, get_password_validators



from BMB_Registration.models import BOOL, GENDER, PRESENTATION, POSITION, TSHIRT_SIZES


from django.forms.utils import ErrorList

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from django import contrib

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

        log.warning('Authenticated User {} is viewing'.format(request.session.get('user')))

        return render(request, 'data.html', )

    else:

        log.warning('AnonymousUser is viewing')

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
                request.session['user']['presentation'] = user.presentation

                user.last_login = datetime.datetime.now()
                user.save()

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

def password_reset(request):


    token_generator = PasswordResetTokenGenerator()

    if request.method == 'POST':
        post_data = request.POST
        form = ResetPasswordForm(post_data)
        if not form.is_valid():
            form.errors['captcha'] = ErrorList(['Invalid captcha'])
            return render(request, 'form.html',
                          {
                              'form' : form
                          },
            )

        email     = post_data['email']
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            message = 'No registration with that email exists!'
            form.errors['email'] = ErrorList([message])
            return render(request, 'form.html',
                          {'form' : form},
            )

        # current_site = get_current_site(request)
        site_name = 'BMB Retreat Registration'
        domain = request.get_host()
        email_template_name = 'password_reset_email.html'
        use_https = False
        c = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': int_to_base36(user.pk),
            'user': user,
            'token': token_generator.make_token(user),
            'protocol': use_https and 'https' or 'http',
        }

        send_mail(
            subject="BMB Retreat Registration Password Reset",
            message=loader.render_to_string(email_template_name, c),
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return render(request, 'password_reset_done.html',
        )

    form = ResetPasswordForm()
    return render(request, 'form.html',
                  {
                      'form' : form,
                      'text_field': 'I am not a robot',
                  },
                )

def password_reset_confirm(request, uidb64=None, token=None):

    token_generator = PasswordResetTokenGenerator()

    uid = force_text(base36_to_int(uidb64))

    user = None
    try:
        user = User._default_manager.get(pk=uid)
        request.session['user'] = dict()
        request.session['user']['first_name'] = user.first_name
        request.session['user']['last_name']  = user.last_name
        request.session['user']['email']      = user.email
        request.session['user']['hide']       = True
        request.session['user']['presentation'] = user.presentation

    except User.DoesNotExist:
        log.warning('User does not exist')
        messages.warning(request, 'User does not exist')
        return HttpResponseRedirect('/')
    except Exception as e:
        log.error(e)
        messages.warning(request, 'Invalid')
        return HttpResponseRedirect('/')


    if request.method == 'POST':
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']

            validators = get_password_validators(AUTH_PASSWORD_VALIDATORS)
            try:
                validate_password(password, password_validators=validators)
            except ValidationError as e:
                message = '\n'.join(e)
                # form = NewPasswordForm()
                form.errors['password2'] = ErrorList([message])
                return render(request, 'password_reset_confirm.html', {'form' : form,
                                                                       'validlink': True
                })

            email = request.session['user']['email']
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            log.info('User {} has successfully reset password'.format(email))

            try:
                request.session.flush()
            except:
                pass

            return render(request,
                          'password_reset_complete.html'
            )

    request.session['user'] = dict()
    log.warning('User : {}'.format(user))
    if user is not None and token_generator.check_token(user, token):
        log.warning('User {} submitted valid token for password reset'.format(user))

        form = NewPasswordForm(request.POST)

        return render(request,
                      'password_reset_confirm.html',
                      {
                          'form': form,
                          'validlink': True,
                      }
        )
    else:
        log.warning('User {} submitted invalid token for password reset'.format(user))
        try:
            request.session.flush()
        except:
            pass
        return render(request,
                      'password_reset_confirm.html',
                      {
                          # 'form': form,
                          'validlink': False,
                      }
        )


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

                messages.success(request, 'Registration info updated successfully.')
                return render(request, 'data.html',
                              {
                                  # 'data' : form.cleaned_data,
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

                validators = get_password_validators(AUTH_PASSWORD_VALIDATORS)
                try:
                    validate_password(post_data.get('password'), password_validators=validators)
                except ValidationError as e:
                    message = '\n'.join(e)
                    form.errors['password2'] = ErrorList([message])
                    return render(request, 'form.html', {'form' : form})

                user = form.save(commit=False)
                password = form.cleaned_data['password']
                user.set_password(password)
                user.save()

                # store user session data and redirect to front page
                request.session['user'] = dict()
                request.session['user']['first_name'] = user.first_name
                request.session['user']['last_name']  = user.last_name
                request.session['user']['email']      = user.email
                request.session['user']['presentation'] = user.presentation


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


            messages.success(request, 'Abstract updated successfully.')
            return render(request, 'data.html',
                        {
                            'page': '/',
                            # 'data': form.cleaned_data,
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



def download(request, target_file):

    # value = request.GET.get('file', '')
    # return HttpResponseRedirect( reverse('download', args=[value]) )


    email = request.session['user']['email']
    user  = User.objects.get(email=email)

    obj = Upload(user=user, upload=target_file)

    full_file = user_directory_path(obj, target_file)

    try:
        instance = Upload.objects.get(user=user, upload=full_file)
    except Exception as e: #
        messages.warning(request, 'File not found')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    savename = full_file.replace(os.sep, '_')

    response = HttpResponse(instance.upload, content_type=mimetypes.guess_type(full_file)[0])
    response['Content-Disposition'] = 'attachment; filename={}'.format(savename)

    return response

def delete(request, target_file):

    email = request.session['user']['email']
    user  = User.objects.get(email=email)

    obj = Upload(user=user, upload=target_file)

    full_file = user_directory_path(obj, target_file)

    try:
        instance = Upload.objects.get(user=user, upload=full_file)
    except Exception as e: #
        messages.warning(request, 'File not found')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    instance.upload.delete()
    instance.delete()
    messages.info(request, 'File {} successfully deleted'.format(target_file))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@user_passes_test(lambda u: u.is_superuser)
def media(request, target_file):


    full_file = os.path.join(MEDIA_ROOT, target_file)
    savename = target_file.replace(os.sep, '_')

    fsock =  open(full_file, 'rb')

    response = HttpResponse(fsock, content_type=mimetypes.guess_type(full_file)[0])
    response['Content-Disposition'] = 'attachment; filename={}'.format(savename)

    return response

    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def within_filesize(f, maxsize=20971520):
    """
    Return True if not too big
    """

    if f is None:
        return False

    print(f._size)

    if f._size > maxsize:
        return 'Please keep filesize under %s. Current filesize %s' % (filesizeformat(maxsize), filesizeformat(f._size))

    return True


def upload_files(request):

    email = request.session['user']['email']
    user  = User.objects.get(email=email)

    records  = Upload.objects.filter(user=user)

    files = sorted([ os.path.basename(record.upload.name) for record in records
                     if bool(record.upload.name)
    ])

    if request.method == 'POST':

        records  = Upload.objects.filter(user=user)
        files = sorted([ os.path.basename(record.upload.name) for record in records
                         if bool(record.upload.name)
        ])

        post_data = request.POST

        myfile = request.FILES.get('upload')
        instance = Upload(user=user, upload=myfile)

        form = UploadForm(post_data, instance=instance)
        print(dir(myfile))

        valid_file = within_filesize(myfile)

        if isinstance(valid_file, str):
            messages.warning(request, valid_file)

        if form.is_valid() and valid_file is True:

            # Submission.objects.filter(user=user).update(**form.cleaned_data)

            Upload.objects.create(user=user, upload=myfile)
            # form.save()

            messages.success(request, 'File updated successfully.')

            records  = Upload.objects.filter(user=user)
            files = sorted([ os.path.basename(record.upload.name) for record in records
                             if bool(record.upload.name)
            ])

            return render(request, 'upload.html',
                          {
                              'form': UploadForm(),
                              'files': files,
                          }
            )

        else:
            return render(request, 'form.html',
                          {
                              'form': UploadForm(),
                              'files': files,
                          }
            )

    return render(request, 'upload.html',
                  {
                      'form': UploadForm(),
                      'files': files,
                  },
    )

def change_password(request):
    if request.method == 'POST':

        post_data     = request.POST
        form = ChangePasswordForm(request.POST)
        email = request.session['user']['email']
        user  = User.objects.get(email=email)

        if post_data.get('password', '') == post_data.get('password2', '') \
           and form.is_valid() :
            old_password  = post_data['old_password']
            if not user.check_password(old_password):
                form.errors['old_password'] = ErrorList(['Invalid Password'])
                return render(request, 'form.html', {'form' : form})

            old_password  = post_data['old_password']
            new_password  = post_data['password']

            validators = get_password_validators(AUTH_PASSWORD_VALIDATORS)
            try:
                validate_password(new_password, password_validators=validators)
            except ValidationError as e:
                message = '\n'.join(e)
                form.errors['password2'] = ErrorList([message])
                return render(request, 'form.html', {'form' : form})


            if old_password == new_password:
                form.errors['password'] = ErrorList(['Must submit a new password'])
                return render(request, 'form.html', {'form' : form})

            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return render(request, 'data.html')

        elif post_data.get('password', '') != post_data.get('password2', ''):
            message = 'Passwords do not match!'
            form.errors['password2'] = ErrorList([message])
        else:
            messages.error(request, 'Please correct the error.')
    else:
        form = ChangePasswordForm()
    return render(request, 'form.html', {
        'form': form
    })

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
