from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url(r'^$', 'task.views.tasks', name='tasks'),
    url(r'^search/$', 'task.views.search_tasks', name='search_tasks'),
    url(r'^new-task/$', 'task.views.new_task', name='new_task'),
    url(r'^complete-task/$', 'task.views.complete_task', name='complete_task'),
    url(r'^uncomplete-task/$', 'task.views.uncomplete_task', name='uncomplete_task'),
    url(r'^hash/(?P<hash>(.*))/$', 'task.views.show_changeset', name='show_changeset'),
)
