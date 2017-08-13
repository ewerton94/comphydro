from furl import furl
import pandas as pd

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import get_language,gettext as _

from data.models import Discretization,Unit,Variable,ConsistencyLevel,OriginalSerie,TemporalSerie
from data.graphs import plot_web
from stats.forms import RollingMeanForm,BasicStatsForm,RateFrequencyOfChangeForm,IHAForm
from .utils import Stats

from .forms import CreateStationForm
from .models import Station, Source, StationType, Localization,Coordinate
from .reads_data import ANA,ONS,Chesf
from .utils import StationInfo,get_stats_list

from plotly.graph_objs import *
from plotly.offline import plot

        
@login_required
def create_station(request):
    if request.method == 'POST':
        form =CreateStationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print("formulário validado")
            station_type = StationType.objects.get(id=data["station_type"])
            source = Source.objects.get(id=data["source"])
            code = data["ana_code"]
            print("code")
            postos = Station.objects.filter(code=code)
            if postos:
                messages.add_message(request, messages.ERROR, _('The station of code: %s already exists into the database.')%postos[0].code)
                return render(request,'create_station.html',{'aba':'map','form':form})  
            print('Solicitando Hidroweb')
            hid = eval(source.source)()
            print(source.source)
            name,localization,erro = hid.obtem_nome_e_localizacao_posto(code)
            if erro:
                messages.add_message(request, messages.ERROR, '%s'%name)
                return render(request,'create_station.html',{'aba':'map','form':form})
            station = Station.objects.create(station_type=station_type,source=source,code=code,name=name, localization=localization)
            station.save()

            for codigo_variavel in range(9,10):
                variavel = Variable.objects.get(ana_code=codigo_variavel)
                executa = hid.executar(station,variavel)
                if executa:
                    messages.add_message(request, messages.ERROR, '%s'%executa) 
            messages.add_message(request, messages.SUCCESS, 'Concluído!')
            return render(request,'create_station.html',{'aba':'map'})    
    form =CreateStationForm
    return render(request,'create_station.html',{'aba':'map','form':form})


def stations(request):
    mpt='pk.eyJ1IjoiYWRlbHNvbmpyIiwiYSI6ImNqNTV0czRkejBnMnkzMnBtdXdsbmRlbDcifQ.Ox8xbLTD_cD7h3uEz13avQ'
    lat=[]
    lon=[]
    text=[]
    stations_ = Station.objects.all()
    context={'BASE_URL':"",'stations':stations}
    if stations_:
        for station in stations_:
            text.append('<a href="/%s/stations/%d/information">%s</a>'%(get_language(),station.id,station))
            lat.append(station.localization.coordinates.y)
            lon.append(station.localization.coordinates.x)

        data=Data([Scattermapbox(lat=lat,lon=lon,mode='markers',marker=Marker(size=14,color='rgb(0, 50, 40)'),text=text,)])
        layout=Layout(autosize=True,margin=Margin(l=0,r=0,b=0,t=0,pad=0),hovermode='closest',mapbox=dict(accesstoken=mpt,bearing=0,center=dict(lat=float(lat[0]),lon=float(lon[0])),pitch=0,zoom=7,),)
        fig=dict(data=data,layout=layout)

        div=plot(fig, auto_open=False, output_type='div')
        context['graph'] = div
    
    return render(request,'stations.html',context)          
 

    

def station_information(request,**kwargs):
    filtros = furl("?"+kwargs['filters']).args
    if 'file' in filtros:
        return HttpResponse("FILE")
    info = StationInfo(kwargs['station_id'],filtros.get('variavel_id',None))
    info.get_originals_graphs_and_temporals()
    variables=[(variable.id,variable.variable) for variable in info.variables]
    if request.method=="POST":
        stats = get_stats_list(request,variables)
        valid_stats = [stat for stat in stats if stat.form.is_valid()]
        if len(valid_stats)>0:
            form = valid_stats[0].form
            data=form.cleaned_data
            url = furl("")
            url.args = {'variable':data['variable'],'discretization':data['discretization']}
            return HttpResponseRedirect("/%s/stats/%s/%s/%s"%(get_language(),valid_stats[0].short_name,kwargs['station_id'],url.url.replace("?","")))
    stats = get_stats_list(request,variables)  
    return render(request,'station_information.html',{'BASE_URL':"",'sources':info.sources,
                                                      'originals':info.originals,
                                                      'station':info.originals[0].station,
                                                      'stats':stats,
                                                      'variables':variables,
                                                     })



