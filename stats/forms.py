# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from data.models import Discretization
from stations.models import Station


class BasicStatsForm(forms.Form):
    def __init__(self, variables=[], *args, **kwargs):
        super(BasicStatsForm, self).__init__(*args, **kwargs)
        self.fields['variable'].choices =list(variables)
        discretizations = ((discretizacao.pandas_code,discretizacao.type) 
                          for discretizacao in Discretization.objects.all() if discretizacao.stats_type.type=="standard")
        self.fields['discretization'].choices =list(discretizations)

    variable = forms.ChoiceField(label=_("Data type")+":",widget=forms.Select(attrs={'class':'form-control'}))
    discretization = forms.ChoiceField(label=_("Discretization")+":",required=False,
                                         widget=forms.Select(attrs={'class':'form-control'}))
 
class RollingMeanForm(forms.Form):
    def __init__(self, variables=[], *args, **kwargs):
        super(RollingMeanForm, self).__init__(*args, **kwargs)
        self.fields['variable'].choices =list(variables)
        rolling_mean_discretizations = ((discretizacao.pandas_code,discretizacao.type)
                          for discretizacao in Discretization.objects.all() if discretizacao.stats_type.type=="rolling mean")
        self.fields['discretization'].choices =list(rolling_mean_discretizations)

    variable = forms.ChoiceField(label=_("Data type")+":",widget=forms.Select(attrs={'class':'form-control'}))
    discretization = forms.ChoiceField(label=_("Discretization")+":",required=False,
                                         widget=forms.Select(attrs={'class':'form-control'}))