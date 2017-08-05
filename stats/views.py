from furl import furl

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render

from data.views import plot_web
from stations.utils import StationInfo
from stations.models import Station, Source, StationType, Localization,Coordinate

from .models import Reduction,ReducedSerie,RollingMeanSerie
from .stats import BasicStats,RollingMean


class StatsView():
    def __init__(self,request,Class):
        self.Class=Class
        self.request=request
        
    def get_data(self,station_id,filters):
        filters = furl("?"+filters).args
        if 'file' in filters:
            return HttpResponse("FILE")
        basic_stats = self.Class(station_id,filters.get('variable'))
        basic_stats.update_informations(
            filters.get('discretization',None),
            filters.get('reduction',None))
        basic_stats.get_or_create_reduced_series()
        return render(self.request,'stats_information.html',{'BASE_URL':"",'sources':basic_stats.sources,
                                                          'reduceds':basic_stats.reduceds,
                                                          'station':basic_stats.station,
                                                          'stats':[],
                                                          'variables':basic_stats.variables,
                                                         })
        

def basic_stats(request,**kwargs):
    stats = StatsView(request,BasicStats)
    return stats.get_data(kwargs['station_id'],kwargs['filters'])



def rolling_mean(request,**kwargs):
    stats = StatsView(request,RollingMean)
    return stats.get_data(kwargs['station_id'],kwargs['filters'])









def station_information(request,**kwargs):
    url = furl("?"+kwargs['filters'])
    filtros = {u[0]:u[1] for u in url.args}
    if 'file' in filtros:
        return HttpResponse("FILE")
    info = StationInfo(kwargs['station_id'])
    if request.method=="POST":
        stats = [
            Stats(_("Rolling Mean"),'rolling_mean',info.variables,RollingMeanForm,request.POST),
            Stats(_("Basic Stats"),'basic_stats',info.variables,BasicStatsForm,request.POST),
        ]
        valid_stats = [stat for stat in stats if stat.form.is_valid()]
        if len(valid_stats)>0:
            form = valid_stats[0].form
            data=form.cleaned_data
            url = furl("")
            url.args = {'var':data['variable'],'dis':data['discretization']}
            
            return HttpResponseRedirect("/%s/stats/%s/%s/%s"%(get_language(),valid_stats[0].short_name,kwargs['station_id'],url.url.replace("?","")))
    stats = [
        Stats(_("Rolling Mean"),'rolling_mean',info.variables,RollingMeanForm),
        Stats(_("Basic Stats"),'basic_stats',info.variables,BasicStatsForm),
    ]  
    return render(request,'station_information.html',{'BASE_URL':"",'sources':info.sources,
                                                      'originals':info.originals,
                                                      'station':info.originals[0].station,
                                                      'stats':stats,
                                                     })