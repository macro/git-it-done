import copy
import urllib
from subprocess import Popen, PIPE

from django.core.urlresolvers import reverse
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings

from task.models import Task


ITEMS_PER_PAGE = 10
class Pages(object):
    def __init__(self, request, queryset, page_size=ITEMS_PER_PAGE, label="items"):
        self.label = label
        self.queryset = queryset
        self.request = request
        self.current_page = int(self.request.GET.get('page', '1'))
        if isinstance(self.queryset, QuerySet):
            self.item_count = self.queryset.count()
        else:
            self.item_count = len(self.queryset)
        self.page_size = page_size if page_size > 0 else self.item_count
        rem = self.item_count % self.page_size
        if rem:
            self.page_count = self.item_count / self.page_size + 1
        else:
            self.page_count = self.item_count / self.page_size

    def _get_range(self, page_num):
        try:
            page_num = int(page_num)
        except ValueError:
            # hack to use pages objects in django templates
            return getattr(self, page_num)(self)

        if self.item_count == 0:
            return 0, 0

        page_num = self.page_count if page_num < 1 else page_num
        page_num = self.page_count if page_num > self.page_count else page_num
        start = (page_num - 1) * self.page_size
        end = page_num * self.page_size
        end = end if end <= self.item_count else self.item_count
        return (start, end)


    def __getitem__(self, page_num):
        """ Returns items on page `page_num`."""
        start, end = self._get_range(page_num)
        return self.queryset[start:end]

    def get_page_items(self):
        """ The items on the current page."""
        return self.__getitem__(self.current_page)

    def get_page_count(self):
        """ The number of pages."""
        return self.page_count

    def get_item_count(self):
        """ The count of all items."""
        return self.item_count

    def page_links(self):
        """ Returns HTML navigation links for pages."""
        if self.item_count == 0:
            return '<div class="page-links"><h4>%d to %d of %d %s</h4></div>' % (
                    0, 0, 0, self.label)
        qd = copy.copy(self.request.GET)
        page_links = []
        # FIXME: show ellipsis for when more than one 25 pages link
        if self.page_count > 1:
            for i in range(1, self.page_count+1):
                qd['page'] = i
                if i != self.current_page:
                    page_links.append('<a href="%s?%s">%d</a>' % (
                                self.request.path, urllib.urlencode(qd), i))
                else:
                    page_links.append('%d' % i)
        start, end = self._get_range(self.current_page)
        return ('<div class="page-links"><h4>%d to %d of %d %s</h4>' % (start+1, end,
                    self.item_count, self.label) + ' | '.join(page_links) + '</div>')

def tasks(request):
    pk = request.REQUEST.get('pk')
    task = None
    if pk:
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            pass
    show_all = bool(request.REQUEST.get('all'))
    if show_all:
       tasks = Task.objects.all()
    else:
       tasks = Task.objects.filter(completed=False)

    page = request.REQUEST.get('page', 1)
    pages = Pages(request, tasks.order_by('-created'), ITEMS_PER_PAGE)
    context = {
        'pages': pages,
        'tasks': pages[page],
        'task': task
    }
    return render_to_response('tasks.html', context)

def search_tasks(request):
    q = unicode.strip(request.REQUEST.get('q'))
    if q:
        tasks = list(set(list(Task.objects.filter(name__icontains=q).order_by('-created')) +
                list(Task.objects.filter(description__icontains=q).order_by('-created'))))
    else:
        tasks = Task.objects.all()

    page = request.REQUEST.get('page', 1)
    pages = Pages(request, tasks, ITEMS_PER_PAGE)
    context = {
        'pages': pages,
        'tasks': pages[page],
        'q': q,
    }
    return render_to_response('tasks.html', context)

def new_task(request):
    name = unicode.strip(request.POST.get('name'))
    description = unicode.strip(request.POST.get('description'))
    pk = request.POST.get('pk')
    if pk:
        task = Task.objects.get(pk=pk)
        task.name = name
        task.description = description
    else:
        task = Task(name=name, description=description)
    task.save()
    return HttpResponseRedirect(reverse('tasks'))

def uncomplete_task(request):
    pk = request.POST.get('pk')
    if pk:
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            pass
        else:
            task.completed = False
            task.save()
    return HttpResponseRedirect(reverse('tasks'))

def complete_task(request):
    pk = request.POST.get('pk')
    h = request.POST.get('hash')
    if pk:
        try:
            task = Task.objects.get(pk=pk)
            if h:
                task.hash = h
        except Task.DoesNotExist:
            pass
        else:
            task.completed = True
            task.save()
    return HttpResponseRedirect(reverse('tasks'))

def shell(cmd, env=None):
    return Popen(cmd, stdout=PIPE, shell=True,
            cwd=settings.GIT_DIR).communicate()[0]

def show_changeset(request, hash):
    changeset = shell('git show %s' % hash)
    context = {
        'changeset': changeset,
    }
    return render_to_response('changeset.html', context)

