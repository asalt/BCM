"""BCM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from BMB_Registration.views import *

urlpatterns = [
    url('^$', home),
    url(r'^admin/', admin.site.urls),
    url(r'^password/$', change_password, name='change_password'),
	url(r'^signup', signup),
    url(r'^update', signup),
    url('^login', login),
    url('^logout', logout),
    url('^abstract', abstract_submission),
    url('^populate_db', populate_db),
    # url(r'^admin/.*/poster_score_form', admin.site.urls)

    # url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),

    # url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^password_reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        password_reset_confirm, name='password_reset_confirm'),
    url(r'^password_reset_done/$', auth_views.password_reset_complete, name='password_reset_complete'),

    url(r'^password_reset/$', password_reset, name='password_reset'),
    # url(r'^password_reset_done/$', password_reset, name='password_reset_done'),

    # url(r'^reset/(?P<uidb36>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     auth_views.password_reset_confirm, name='password_reset_confirm'),

    # url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     auth_views.password_reset_confirm,
    #     name='password_reset_confirm'),

    # url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    # url(r'^accounts/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
    # url(r'^accounts/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm',
    # url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     auth_views.password_reset_confirm, name='password_reset_confirm'),

    # url(r'^/password_reset_complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    # url(r'^/password_reset_done/$', auth_views.password_reset_complete, name='password_reset_complete'),

]
