# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from RandoAmisSecours.models import Outing

        
class OutingForm(forms.ModelForm):
    """ Form class for creating a new Outing
    """
    name = forms.CharField(
        required=True, label=_("Name"),
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': _('Outing name'),
            'autofocus': 'autofocus',
        })
    )
    description = forms.CharField(
        required=True, label=_("Description"),
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'placeholder': _('Description'),
        })
    )

    latitude = forms.FloatField(
        required=True, label=_("Latitude"),
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': _('Latitude'),
        })
    )
    longitude = forms.FloatField(
        required=True, label=_("Longitude"),
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': _('Longitude'),
        })
    )
    beginning = forms.DateTimeField(
        required=True, label=_("Begin"), input_formats=['%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control'
        })
    )
    ending = forms.DateTimeField(
        required=True, label=_("End"), input_formats=['%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control'
        })
    )
    alert = forms.DateTimeField(
        required=True, label=_("Alert"), input_formats=['%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = Outing
        exclude = ('user', 'status',)

    def __init__(self, *args, **kwargs):
        super(OutingForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(OutingForm, self).clean()
        beginning = cleaned_data.get('beginning')
        ending = cleaned_data.get('ending')
        alert = cleaned_data.get('alert')

        if beginning and ending and alert:
            if beginning >= ending or ending >= alert:
                self._errors['beginning'] = self.error_class(
                    [_('Beginning should happens first')]
                )
                self._errors['ending'] = self.error_class(
                    [_('Ending should happens after the beginning')]
                )
                self._errors['alert'] = self.error_class(
                    [_('Alert should happens at the end')]
                )
                del cleaned_data['beginning']
                del cleaned_data['ending']
                del cleaned_data['alert']

        return cleaned_data
