from plotly.offline import plot
from plotly.graph_objs import Scatter, Figure, Layout

from django.shortcuts import render
from django.http import HttpResponse
from django.utils.translation import gettext as _



def plot_web(xys,title,variable,unit,names=[]):
    data=[Scatter(x=xy[0], y=xy[1]) for xy in xys]
    if names:
        for i in range(len(data)):
            data[i].name=names[i]
    return plot({
                    'data':data,
                    'layout':Layout(title=title,xaxis={'title':_('time')},yaxis={'title':"%s (%s)"
                                                                                      %(str(variable),
                                                                                        str(unit))})

                },auto_open=False, output_type='div')

def home(request):
    return render(request,'home.html',{})