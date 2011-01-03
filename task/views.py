import copy
import urllib

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from task.models import Task


ITEMS_PER_PAGE = 10

class Pages(object):
    def __init__(self, request, items, page_size):
        self.items = items
        self.request = request
        self.item_count = len(self.items)
        self.page_size = page_size if page_size > 0 else self.item_count
        rem = self.item_count % self.page_size
        if rem:
            self.page_count = self.item_count / self.page_size + 1
        else:
            self.page_count = self.item_count / self.page_size

    def __getitem__(self, page_num):
        try:
            page_num = int(page_num)
        except ValueError:
            # hack to use pages objects in django templates
            return getattr(self, page_num)(self)

        if self.item_count == 0:
            return []

        page_num = self.page_count if page_num < 1 else page_num
        page_num = self.page_count if page_num > self.page_count else page_num
        start = (page_num - 1) * self.page_size
        end = page_num * self.page_size
        return self.items[start:end]

    def get_page_count(self):
        return self.page_count

    def get_item_count(self):
        return self.item_count

    def page_links(self):
        if self.item_count == 0:
            return ''
        qd = copy.copy(self.request.GET)
        page_links = []
        for i in range(1, self.page_count+1):
            qd['page'] = i
            page_links.append('<a href="%s?%s">%d</a>' % (self.request.path,
                        urllib.urlencode(qd), i))

        return ('<h3>%d tasks</h3>' % (self.item_count,) +
                ' | '.join(page_links))

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
    if pk:
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            pass
        else:
            task.completed = True
            task.save()
    return HttpResponseRedirect(reverse('tasks'))

