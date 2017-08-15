from furl import furl
import pandas as pd

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import get_language,gettext as _

from data.models import Discretization,Unit,Variable,ConsistencyLevel,OriginalSerie,TemporalSerie
from data.graphs import plot_web
from stats.forms import RollingMeanForm,BasicStatsForm,RateFrequencyOfChangeForm
#from stats.stats import Stats

from .forms import CreateStationForm
from .models import Station, Source, StationType, Localization,Coordinate
from .reads_data import ANA,ONS


class Stats(object):
    def __init__(self,request,name,short_name,variables,form):
        data = request.POST if short_name in request.POST else None
        self.name = name        
        self.form=form(variables=variables,data=data,prefix=short_name)
        self.short_name=short_name
        
def get_stats_list(request,variables):
    return [
            Stats(request,_("Rolling Mean"),'rolling_mean',variables,RollingMeanForm),
            Stats(request,_("Basic Stats"),'basic_stats',variables,BasicStatsForm),
            Stats(request,_("Rate of change"),'rate_of_change',variables,RateFrequencyOfChangeForm),
            Stats(request,_("Frequency of change"),'frequency_of_change',variables,RateFrequencyOfChangeForm),
            Stats(request,_("Indicators of Hydrologic Alterations"),'iha',variables,RateFrequencyOfChangeForm),
            Stats(request,_("Julian Date"),'julian_date',variables,RateFrequencyOfChangeForm),
            Stats(request,_("Pulse Count"),'pulse_count',variables,RateFrequencyOfChangeForm),
            Stats(request,_("Pulse Duration"),'pulse_duration',variables,RateFrequencyOfChangeForm),
            Stats(request,_("Reference Flow"),'reference_flow',variables,RateFrequencyOfChangeForm),
        ]

class StationInfo(object):
    def __init__(self,station_id,*variables):
        self.station=Station.objects.get(id=station_id)
        if variables:
            self.variable_ids=list(map(int,[v for v in variables if not v is None]))
        
        
    def update_originals(self,Serie=OriginalSerie):
        if self.variable_ids:
            self.originals = OriginalSerie.objects.filter(station=self.station)
            self.originals.filter(variable__id__in=self.variable_ids)
        else:
            self.originals = OriginalSerie.objects.filter(station=self.station)
    def update_variables_and_sources(self):
        if self.variable_ids:
            self.variables=Variable.objects.filter(id__in=self.variable_ids)
        else:
            self.variables=list(set([o.variable for o in self.originals]))
        self.sources=list(set([o.station.source for o in self.originals]))
        return self.originals,self.variables,self.sources
    def create_daily_data_pandas(self,temporals):
        self.temporals = temporals
        data = [o.data if not o is None else nan for o in temporals]
        date = [o.date for o in temporals]
        pf = pd.DataFrame({"data" : data}, index=pd.DatetimeIndex(date))
        gp = pd.Grouper(freq='D',sort=True)
        self.daily_data = pf.groupby(gp).mean()
        return self.daily_data
    def create_graph(self,xys,variable,unit):
        return plot_web(xys=xys,
                                      title="%s"%(str(variable)),
                                        variable=variable,unit=unit)
    def get_originals_graphs_and_temporals(self):
        self.update_originals()
        self.update_variables_and_sources()
        for original in self.originals:
            temporals = TemporalSerie.objects.filter(id=original.temporal_serie_id) 
            original.temporals = temporals
            daily_data=self.create_daily_data_pandas(temporals)
            self.xys=[[daily_data.index,daily_data['data'].values],]
            original.graph = self.create_graph(self.xys,original.variable,original.unit)
            
            
            