from django.conf.urls import patterns, include, url
import mailbot.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mailbot.views.home', name='home'),
    # url(r'^mailbot/', include('mailbot.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^index/', mailbot.views.index),
    url(r'^add_message/', mailbot.views.add_message),
    url(r'^add_account/', mailbot.views.add_account),
    url(r'^get_messages/', mailbot.views.get_messages),
    url(r'^get_accounts/', mailbot.views.get_accounts),
    url(r'^add_account_group/', mailbot.views.add_account_group),
    url(r'^get_groups/', mailbot.views.get_groups),
    url(r'^add_account_to_group/', mailbot.views.add_account_to_group),
    url(r'^delete_account/', mailbot.views.delete_account),
    url(r'^send_msg_to_group/', mailbot.views.send_msg_to_group),
)
