from django.conf.urls import patterns, url

from api import views

urlpatterns = patterns('',
    url(r'^workflows$',     views.workflows,     name='workflows'),
    url(r'^jobs$',          views.jobs,          name='jobs'),
    url(r'^job_instances$', views.job_instances, name='job_instances'),
    url(r'^artifact$',      views.get_file,      name='artifact'),

    url(r'^submitfile$',    views.submitfile,    name='submitfile'),
    url(r'^dagman$',        views.dagman,        name='dagman'),
    url(r'^dagmanout$',     views.dagmanout,     name='dagmanout'),
)

