from plotly.offline import plot
from plotly.graph_objs import Scatter, Figure, Layout

from django.shortcuts import render
from django.http import HttpResponse
from django.utils.translation import gettext as _



def plot_web(xys,title,variable,unit,names=[],xaxis_title=_('time')):
    data=[Scatter(x=xy[0], y=xy[1]) for xy in xys]
    if names:
        for i in range(len(data)):
            data[i].name=names[i]
    return plot({
                    'data':data,
        
                    'layout':Layout(title=title,xaxis={'title':xaxis_title},yaxis={'title':"%s (%s)"
                                                                                      %(str(variable),
                                                                                        str(unit))})

                },auto_open=False, output_type='div')

def home(request):
    return render(request,'home.html',{})



def plot_polar(xys,title,variable,unit,names=[]):
    data=[Scatter(t=[d.strftime("%Y") for d in xy[0]], r=xy[1],mode='lines+markers',marker=dict(opacity=0.7)) for xy in xys]
    if names:
        for i in range(len(data)):
            data[i].name=names[i]
    return plot({
                    'data':data,
                    'layout':Layout(title=title,orientation=-90,xaxis={'title':_('time')},)

                },auto_open=False, output_type='div')
    #layout=go.Layout(title='Maximos e minimos',orientation=-90)
    #fig=go.Figure(data=data,layout=layout)
    #div=plot(fig,auto_open=False, output_type='div')
    #return div
