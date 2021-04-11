from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from django.views.generic.edit import UpdateView, CreateView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from apps.main.users.decorators import superuser_required

from apps.main.notifications.models import Notifications
from apps.main.refectories.models import Refectory
from apps.main.users.models import CustomUser

@method_decorator([login_required, superuser_required], name='dispatch')
class NotificationListView(ListView):
    model = Notifications
    template_name = 'notifications/notifications_list.html'

    def get_queryset(self):
        queryset = Notifications.objects.filter(user_notification_id=self.request.user.id)
        return queryset

class NotificationListViewGuest(ListView):
    model = Notifications
    template_name = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = Notifications.objects.filter(refectory_id=self.request.user.profile.refectory.id, user_notification_id=self.request.user.id)
        
        context['object_list'] = []
        for i in query:
            context['object_list'].append({
                    'id':i.id,
                    'notification_type':i.notification_type,
                    'notification_message':i.notification_message,
                    'read':i.read,
                    'created':i.created,
            })      
        return context

class NotificationCount(View):
    def get(self, request, *args, **kwargs):
        query = Notifications.objects.filter(user_notification_id=self.request.user.id,read=False)
        return len(query)

def UpdateNotificationRead(request, pk):
    notifications_id = pk
    query = Notifications.objects.get(id=notifications_id)
    query.read = True
    query.save()
    if request.user.is_superuser:
        return HttpResponseRedirect("/dashboard/notifications/notifications-admin")
    else:
        return HttpResponseRedirect("/dashboard/notifications/notifications-user")


def UpdateNotificationStatus(request, pk):
    notifications_id = pk
    query = Notifications.objects.get(id=notifications_id)
    query.status = 'Solucionado'
    query.save()

    notifications_list = Notifications.objects.filter(refectory_id=query.refectory_id,status='Pendiente',notification_message=query.notification_message)
    for i in notifications_list:
        i.status = 'Solucionado'
        i.save()

    if request.user.is_superuser:
        return HttpResponseRedirect("/dashboard/notifications/notifications-admin")
    else:
        return HttpResponseRedirect("/dashboard/notifications/notifications-user")