from django.conf.urls import patterns, url

from api import views

urlpatterns = patterns (
    '',
    url(r'^flows/(?P<name_filter>(\w+))/(?P<status_filter>(\w+))/$',
        views.flows,         name='flows'),

    url(r'^jobs/(?P<flow>(.*))/$',
        views.jobs,          name='jobs'),

    url(r'^job_instances$',
        views.job_instances, name='job_instances'),

    url(r'^artifact/(?P<pattern>(\d))/(?P<page>(\d+))/(?P<tag>(.*))/$',
        views.get_file,      name='artifact'),

    url(r'^addflow/(?P<flow_name>(\w+))/$',
        views.add_flow,      name='add_flow'),

    url(r'^listflows/(?P<current_id>(\w+))/(?P<target_page>(\d+))/(?P<page_size>(\d+))/$',
        views.list_flows,    name='list_flows'),
    )

