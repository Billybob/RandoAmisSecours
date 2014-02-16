# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2013 Rémi Duraffort
# This file is part of RandoAmisSecours.
#
# RandoAmisSecours is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RandoAmisSecours is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with RandoAmisSecours.  If not, see <http://www.gnu.org/licenses/>

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic import FormView, UpdateView, DeleteView

from RandoAmisSecours.forms import OutingForm
from RandoAmisSecours.mixins import OutingMixin
from RandoAmisSecours.models import Outing, DRAFT, CONFIRMED, FINISHED


@login_required
def index(request):
    # List all outings owned by the user and his friends
    user_outings = Outing.objects.filter(user=request.user)
    user_outings_confirmed = user_outings.filter(status=CONFIRMED)
    user_outings_draft = user_outings.filter(status=DRAFT)
    user_outings_finished = user_outings.filter(status=FINISHED)

    friends_outings = Outing.objects.filter(user__profile__in=request.user.profile.friends.all()).select_related()
    friends_outings_confirmed = friends_outings.filter(status=CONFIRMED)
    friends_outings_draft = friends_outings.filter(status=DRAFT)
    friends_outings_finished = friends_outings.filter(status=FINISHED)

    return render_to_response('RandoAmisSecours/outing/index.html',
                              {'user_outings_confirmed': user_outings_confirmed,
                               'user_outings_draft': user_outings_draft,
                               'user_outings_finished': user_outings_finished,
                               'friends_outings_confirmed': friends_outings_confirmed,
                               'friends_outings_draft': friends_outings_draft,
                               'friends_outings_finished': friends_outings_finished},
                              context_instance=RequestContext(request))


@login_required
def details(request, outing_id):
    # Return 404 if the outing does not belong to the user or his friends
    outing = get_object_or_404(Outing, Q(user=request.user) | Q(user__profile__in=request.user.profile.friends.all()), pk=outing_id)

    return render_to_response('RandoAmisSecours/outing/details.html',
                              {'outing': outing,
                               'FINISHED': FINISHED,
                               'CONFIRMED': CONFIRMED,
                               'DRAFT': DRAFT},
                              context_instance=RequestContext(request))


class OutingCreate(FormView):
    """ Create a new Outing
    """
    model = Outing
    form_class = OutingForm
    template_name = 'RandoAmisSecours/outing/create.html'
    messages = {
        "create_success": {
            "level": messages.SUCCESS,
            "text": _(u"Outing successfully created. The outing is still a draft and should be confirmed.")
        },
    }

    def get_form_kwargs(self):
        kwargs = super(OutingCreate, self).get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        if self.messages.get("create_success"):
            messages.add_message(
                self.request,
                self.messages["create_success"]["level"],
                self.messages["create_success"]["text"]
            )

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("outings.details", kwargs={'outing_id': self.object.pk})


class OutingUpdate(OutingMixin, UpdateView):
    """ Update a outing
    """
    template_name = "RandoAmisSecours/outing/create.html"
    form_class = OutingForm
    messages = {
        "update_success": {
            "level": messages.SUCCESS,
            "text": _(u"Outing successfully update.")
        },
        "permission_denied": {
            "level": messages.WARNING,
            "text": _(u"Only the outing owner can update it.")
        }
    }

    def get_form_kwargs(self):
        kwargs = super(OutingUpdate, self).get_form_kwargs()
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(OutingUpdate, self).get_context_data(**kwargs)
        ctx['update'] = True
        return ctx

    def get(self, request, *args, **kwargs):
        """ Get Outing to update
        """
        self.object = self.get_outing()

        if self.object.status == FINISHED:
            raise Http404

        if self.object.user != self.request.user:
            if self.messages.get("permission_denied"):
                messages.add_message(
                    self.request,
                    self.messages["permission_denied"]["level"],
                    self.messages["permission_denied"]["text"]
                )

            return HttpResponseRedirect(self.get_success_url())

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        ctx = RequestContext(
            self.request, self.get_context_data(form=form)
        )
        return UpdateView.render_to_response(self, ctx)

    def get_success_url(self):
        return reverse("outings.details", kwargs={
            'outing_id': self.object.pk
        })


class OutingDelete(OutingMixin, DeleteView):
    """ Delete a outing
    """
    messages = {
        "delete_success": {
            "level": messages.SUCCESS,
            "text": _(u"Outing «%(name)s» successfully delete.")
        },
        "permission_denied": {
            "level": messages.WARNING,
            "text": _(u"Only the outing owner can delete it.")
        }
    }

    def get(self, request, **kwargs):
        self.object = self.get_outing()

        if self.object.user != self.request.user:
            if self.messages.get("permission_denied"):
                messages.add_message(
                    self.request,
                    self.messages["permission_denied"]["level"],
                    self.messages["permission_denied"]["text"]
                )

        else:
            self.object.delete()

            if self.messages.get("delete_success"):
                messages.add_message(
                    self.request,
                    self.messages["delete_success"]["level"],
                    self.messages["delete_success"]["text"] % {
                        "name": self.object.name
                    }
                )

        return HttpResponseRedirect(reverse("outings.index"))


@login_required
def confirm(request, outing_id):
    outing = get_object_or_404(Outing, pk=outing_id)
    if outing.user != request.user:
        messages.error(request, _('Only the outing owner can update it'))
        return HttpResponseRedirect(reverse('outings.index'))

    outing.status = CONFIRMED
    outing.save()
    messages.success(request, _("«%(name)s» is now confirmed") % ({'name': outing.name}))
    return HttpResponseRedirect(reverse('outings.index'))


@login_required
def finish(request, outing_id):
    outing = get_object_or_404(Outing, pk=outing_id)
    if outing.user != request.user:
        messages.error(request, _('Only the outing owner can finish it'))
        return HttpResponseRedirect(reverse('outings.index'))

    outing.status = FINISHED
    outing.save()
    messages.success(request, _("«%(name)s» is now finished") % ({'name': outing.name}))
    return HttpResponseRedirect(reverse('outings.index'))
