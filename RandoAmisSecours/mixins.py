
from django.shortcuts import get_object_or_404

from RandoAmisSecours.models import Outing


class OutingMixin(object):
    outing_model = Outing
    outing_context_name = 'outing'

    def get_outing_model(self):
        return self.outing_model

    def get_context_data(self, **kwargs):
        kwargs.update({self.outing_context_name: self.get_outing()})
        return super(OutingMixin, self).get_context_data(**kwargs)

    def get_object(self):
        if hasattr(self, 'outing'):
            return self.outing
        outing_id = self.kwargs.get('outing_id', None)
        self.outing = get_object_or_404(
            self.get_outing_model(), id=outing_id
        )
        return self.outing
    get_outing = get_object  # Now available when `get_object` is overridden
