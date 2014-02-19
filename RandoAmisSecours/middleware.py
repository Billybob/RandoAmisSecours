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
import pytz

from django.utils import timezone, translation
from django.utils.cache import patch_vary_headers


class LocaleMiddleware(object):
    """
        MIDDLEWARE_CLASSES = [
            ...
            "RandoAmisSecours.middleware.LocaleMiddleware",
            ...
        ]
    """
    
    def get_language_for_user(self, request):
        if request.user.is_authenticated():
            try:
                profile = Profile.objects.get(user=request.user)
                return profile.language
            except Profile.DoesNotExist:
                pass
        return translation.get_language_from_request(request)
    
    def process_request(self, request):
        translation.activate(self.get_language_for_user(request))
        request.LANGUAGE_CODE = translation.get_language()
    
    def process_response(self, request, response):
        patch_vary_headers(response, ("Accept-Language",))
        response["Content-Language"] = translation.get_language()
        translation.deactivate()
        return response
        
        
class TimezoneMiddleware(object):
    def process_request(self, request):
        tz = request.session.get('django_timezone')
        if tz:
            timezone.activate(pytz.timezone(tz))
        else:
            timezone.deactivate()
