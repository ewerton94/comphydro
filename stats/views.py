from furl import furl

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render

from data.graphs import plot_web
from stations.utils import StationInfo,get_stats_list
from stations.models import Station, Source, StationType, Localization,Coordinate
from data.models import Variable
from datetime import datetime

from .models import Reduction,ReducedSerie,RollingMeanSerie
from .stats import BasicStats,RollingMean,RateOfChange,FrequencyOfChange,IHA,JulianDate
import pandas as pd


def export_xls(reduceds,stats_name):
    import xlwt
    response = HttpResponse(content_type ='application/ms-excel')
    filename='%s.xls'%stats_name
    response['Content-Disposition'] = 'attachment; filename=%s'%filename
    wb = xlwt.Workbook(encoding='utf-8')
    for reduced in reduceds:
        ws = wb.add_sheet(str(reduced.discretization)+str(reduced.variable))
        row_num = 0
        columns = []
        [columns.extend([('date',6000),(name,6000)]) for name in reduced.names]
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num][0], font_style)
            # set column width
            ws.col(col_num).width = columns[col_num][1]

        font_style = xlwt.XFStyle()
        font_style.alignment.wrap = 1
        date_style=xlwt.XFStyle()
        date_style.num_format_str = 'dd/mm/yyyy'
        col_num = 0
        row_num += 1
        aux=row_num
        first=True
        for xy in reduced.xys:
            x,y = xy
            xy=list(zip(x,y))
            for row_num in range(len(x)):
                date=pd.to_datetime(xy[row_num][0],utc=True)
                ws.write(row_num+aux, col_num, datetime(date.year,date.month,date.day), date_style)
                ws.write(row_num+aux, col_num+1, xy[row_num][1], font_style)
            col_num+=2
    wb.save(response)
    return response

class StatsView():
    def __init__(self,request,Class):
        self.Class=Class
        self.request=request
        
    def get_data(self,station_id,stats_name,filters):
        filters = furl("?"+filters).args
        basic_stats = self.Class(station_id,filters.get('variable'))
        basic_stats.update_informations(
            filters.get('discretization',None),
            filters.get('reduction',None),
            stats_name
        )
        basic_stats.get_or_create_reduced_series()
        if 'file' in filters:
            return export_xls(basic_stats.reduceds,stats_name)
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
    flow = Variable.objects.get(variable_en_us="flow")
    
    g = IHA(kwargs['station_id'],
            kwargs['other_id'],
            filters.get('variable',flow.id),
            filters.get('start_year',None),
            filters.get('end_year',None),
            
           )
    group1=g.Group1()
    group2=g.Group2()
    group3=g.Group3()
    group4=g.Group4()
    group5=g.Group5()
    sources=set([g.station.source,g.other.source])
    return render(request,'iha.html',{'BASE_URL':"",'station':g.station,
                                                             'aba':"IHA",
                                      'sources':sources,
                                      'stats':get_stats_list(request,[g.variable,]),
                                           'group1':group1,
                                           'group2':group2,
                                           'group3':group3,
                                           'group4':group4,
                                           'group5':group5,
                                                         })
    