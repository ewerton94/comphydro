# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from data.models import Discretization,OriginalSerie
from stations.models import Station
 
    

class GenericStatsForm(forms.Form):
    def __init__(self, variables=[],stats_type="standard", *args, **kwargs):
        super(GenericStatsForm, self).__init__(*args, **kwargs)
        self.fields['variable'].choices =list(variables)
        ds = Discretization.objects.filter(stats_type__type=stats_type)
        if not ds:
            ds=Discretization.objects.filter(stats_type__type="standard")
        discretizations = ((discretizacao.pandas_code,discretizacao.type) 
                          for discretizacao in ds)
        self.fields['discretization'].choices =list(discretizations)

    variable = forms.ChoiceField(label=_("Data type")+":",widget=forms.Select(attrs={'class':'form-control'}))
    discretization = forms.ChoiceField(label=_("Discretization")+":",required=False,
                                         widget=forms.Select(attrs={'class':'form-control'}))
    
    
class AnnualStatsForm(forms.Form):
    def __init__(self, variables=[],stats_list=[], *args, **kwargs):
        super(AnnualStatsForm, self).__init__(*args, **kwargs)
        self.fields['variable'].choices =list(variables)
        self.fields['stats'].choices =list(stats_list)
        

    variable = forms.ChoiceField(label=_("Data type")+":",widget=forms.Select(attrs={'class':'form-control'}))
    stats = forms.ChoiceField(label=_("Stats")+":",required=False,
                                         widget=forms.Select(attrs={'class':'form-control'}))
    


    
    
class IHAForm(forms.Form):
    def __init__(self, variables=[],stats_type="standard", *args, **kwargs):
        super(IHAForm, self).__init__(*args, **kwargs)
    station = forms.ChoiceField(label=_("Station to compare")+":",widget=forms.Select(attrs={'class':'form-control'}),choices=
                                 ((o.id,o) for o in Station.objects.all())
                                )
    initial = forms.CharField(label=_("Initial year")+":",widget=forms.TextInput(attrs={'class':'form-control'}))
    final = forms.CharField(label=_("Final year")+":",widget=forms.TextInput(attrs={'class':'form-control'}))