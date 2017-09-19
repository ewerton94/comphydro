# -*- coding: utf-8 -*-
from furl import furl

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render

from data.graphs import plot_web
from stations.utils import StationInfo,get_stats_list,get_all_stats_form_list,get_annual_stats_form_list,get_standard_stats_form_list,get_specific_stats_form_list
from stations.models import Station, Source, StationType, Localization,Coordinate
from data.models import Variable
from datetime import datetime

from .models import Reduction,ReducedSerie,RollingMeanSerie
from .stats import BasicStats,RollingMean,RateOfChange,FrequencyOfChange,IHA,JulianDate,PulseCount,PulseDuration,ReferenceFlow,cv
import pandas as pd
from django.views import View


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
        basic_stats = self.Class(station_id,filters.get('variable',None))
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
                                                          'all_stats':get_all_stats_form_list(),
                                                             'aba':"_".join(stats_name.split()),
                                                  
                                                    
                                                         })
  

def stats_view(request,stats_name,**kwargs):
    if stats_name in [e[0] for e in get_specific_stats_form_list()]:
        return eval(stats_name)(request,**kwargs)
    class_name = stats_name.title().replace("_","")
    stats = StatsView(request,eval(class_name))
    if stats_name in [e[0] for e in get_standard_stats_form_list()]:
        return stats.get_data(kwargs['station_id'],stats_name.replace("_"," "),kwargs['filters'])
    if stats_name in [e[0] for e in get_annual_stats_form_list()]:
        if 'discretization' in kwargs['filters']:
            kwargs['filters']=kwargs['filters'].split('discretization')[0]+"discretization=A"
        else:
            kwargs['filters']+="discretization=A"
        return stats.get_data(kwargs['station_id'],stats_name.replace("_"," "),kwargs['filters'])
    else:
        return HttpResponse("Stats not found")
    
  
        




def iha(request,**kwargs):
    filters = furl("?"+kwargs['filters']).args
    flow = Variable.objects.get(variable_en_us="flow")
    
    g = IHA(kwargs['station_id'],
            filters.get('other_id',kwargs['station_id']),
            filters.get('variable',flow.id),
            filters.get('start_year',None),
            filters.get('end_year',None),
            
           )
    group1=g.Group1()
    group1cv=g.Group1cv()
    group2cv,graphscv=g.Group2cv()
    group2,graphs2=g.Group2()
    '''
    reference_flow,graph_rf=g.ReferenceFlow()
    graphs2.append(graph_rf)
    '''
    #Group 3 - Period of extremes
    classes={'julian date':JulianDate}
    group3=g.Group(classes)
    group3cv=g.Group(classes,function_reduce=cv)
    #Group 4 - Pulses
    classes={'pulse count':PulseCount,'pulse duration':PulseDuration}
    group4=g.Group(classes,calculate_limiar=True)
    group4cv=g.Group(classes,function_reduce=cv,calculate_limiar=True)
    #Group 5 - Rate and Frequency of change
    classes={'frequency of change':FrequencyOfChange,'rate of change':RateOfChange}
    group5=g.Group(classes)
    group5cv=g.Group(classes,function_reduce=cv,calculate_limiar=True)
    #sources
    sources=set([g.station.source,g.other.source])
    return render(request,'iha.html',{'BASE_URL':"",'station':g.station,
                                                             'aba':"IHA",
                                      'sources':sources,
                                      'stats':get_stats_list(request,[g.variable,]),
                                           'group1':group1,
                                           'group1cv':group1cv,
                                           'group2':group2,
                                           'group2cv':group2cv,
                                           'group3':group3,
                                           'group3cv':group3cv,
                                           'group4':group4,
                                           'group4cv':group4cv,
                                           'group5':group5,
                                           'group5cv':group5cv,
                                      #'graphs':graphs2,
                                      #'reference_flow':reference_flow,
                                      'all_stats':get_all_stats_form_list(),
                                                         })
    