from furl import furl

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render

from data.views import plot_web
from stations.utils import StationInfo,get_stats_list
from stations.models import Station, Source, StationType, Localization,Coordinate

from .models import Reduction,ReducedSerie,RollingMeanSerie
from .stats import BasicStats,RollingMean,RateOfChange,FrequencyOfChange,IHA,JulianDate


class StatsView():
    def __init__(self,request,Class):
        self.Class=Class
        self.request=request
        
    def get_data(self,station_id,stats_name,filters):
        filters = furl("?"+filters).args
        if 'file' in filters:
            return HttpResponse("FILE")
        basic_stats = self.Class(station_id,filters.get('variable'))
        basic_stats.update_informations(
            filters.get('discretization',None),
            filters.get('reduction',None),
            stats_name
        )
        basic_stats.get_or_create_reduced_series()
        return render(self.request,'stats_information.html',{'BASE_URL':"",'sources':basic_stats.sources,
                                                          'reduceds':basic_stats.reduceds,
                                                          'station':basic_stats.station,
                                                          'stats':get_stats_list(self.request,[]),
                                                             'aba':"_".join(stats_name.split()),
                                                    
                                                         })
        

def basic_stats(request,**kwargs):
    stats = StatsView(request,BasicStats)
    return stats.get_data(kwargs['station_id'],'basic stats',kwargs['filters'])

def rolling_mean(request,**kwargs):
    stats = StatsView(request,RollingMean)
    return stats.get_data(kwargs['station_id'],'rolling mean',kwargs['filters'])

def rate_of_change(request,**kwargs):
    stats = StatsView(request,RateOfChange)
    if 'discretization' in kwargs['filters']:
        kwargs['filters']=kwargs['filters'].split('discretization')[0]+"discretization=A"
    else:
        kwargs['filters']+="discretization=A"
    return stats.get_data(kwargs['station_id'],'rate of change',kwargs['filters'])

def frequency_of_change(request,**kwargs):
    stats = StatsView(request,FrequencyOfChange)
    if 'discretization' in kwargs['filters']:
        kwargs['filters']=kwargs['filters'].split('discretization')[0]+"discretization=A"
    else:
        kwargs['filters']+="discretization=A"
    return stats.get_data(kwargs['station_id'],'frequency of change',kwargs['filters'])

def julian_date(request,**kwargs):
    stats = StatsView(request,JulianDate)
    if 'discretization' in kwargs['filters']:
        kwargs['filters']=kwargs['filters'].split('discretization')[0]+"discretization=A"
    else:
        kwargs['filters']+="discretization=A"
    return stats.get_data(kwargs['station_id'],'julian date',kwargs['filters'])

def iha(request,**kwargs):
    filters = furl("?"+kwargs['filters']).args
    g = IHA(kwargs['station_id'],kwargs['station_id'],filters.get('variable',1))
    group1=g.Group1()
    group2=g.Group2()
    sources=set([g.station.source,g.other.source])
    return render(request,'iha.html',{'BASE_URL':"",'station':g.station,
                                                             'aba':"IHA",
                                      'sources':sources,
                                      'stats':get_stats_list(request,[g.variable,]),
                                           'group1':group1,
                                           'group2':group2
                                                         })
    