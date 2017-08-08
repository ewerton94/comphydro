import pandas as pd
from numpy import nan,mean,argmax,argmin,where,split
from datetime import datetime
from abc import ABCMeta, abstractmethod
from django.utils.translation import gettext as _
from data.models import Discretization,Unit,Variable,ConsistencyLevel,OriginalSerie,TemporalSerie,Stats
from data.views import plot_web
from stations.reads_data import get_id_temporal,criar_temporal
from stations.models import Station
from stations.utils import StationInfo
from .models import Reduction,ReducedSerie,RollingMeanSerie



        

        
funcoes_reducao = {'máxima':max,'mínima':min,'soma':sum, 'média':mean,'máxima média móvel':argmax,
                   'mínima média móvel':argmin,'fall rate':'<','rise rate':'>','fall count':'<','rise count':'>'}
meses = {1:"JAN",2:"FEB",3:"MAR",4:"APR",5:"MAY",6:"JUN",7:"JUL",8:"AUG",9:"SEP",10:"OCT",11:"NOV",12:"DEC"}


def get_originals(variables,originals):
    os=[]
    for variable in variables:
        originals_by_variable=[o for o in originals if o.variable==variable]
        id_data_type = 2 if 2 in [o.consistency_level.id for o in originals_by_variable] else 1
        os.append([o for o in originals_by_variable if o.consistency_level.id == id_data_type][0])
    return os


class Table:
    def __init__(self,title,pre_data,pos_data):
        self.title=title
        self.pre_data=pre_data
        self.pos_data=pos_data
        self.deviation_magnitude = pre_data-pos_data
        self.percent = int(self.deviation_magnitude/pre_data*100)
        
    def __str__(self):
        return str(self.title)+"  -  "+str(self.value)

class generic_obj:
    pass
        
def get_available_variables(station):
    return [o.variable for o in OriginalSerie.objects.filter(station=station)]

class BaseStats(StationInfo,metaclass=ABCMeta):
    def update_informations(self,discretization_code=None,reduction_id=None,stats_type='standard'):
        if discretization_code is None:
            self.discretizations=Discretization.objects.all()
            self.discretizations=[d for d in self.discretizations if d.stats_type.type==stats_type]
        else:
            self.discretizations = Discretization.objects.filter(pandas_code=discretization_code)
        if reduction_id==None:
            self.reductions =Reduction.objects.filter(stats_type__type=stats_type)
        else:
            self.reductions = Reduction.objects.filter(id=reduction_id)
    
    def update_originals(self):
        super(BaseStats,self).update_originals()
        self.update_variables_and_sources()
        self.originals=get_originals(self.variables,self.originals)
        return self.originals

    def starting_month_hydrologic_year(self,df):
        mean_by_month = df["data"].groupby(pd.Grouper(freq='M')).mean()
        years_minimum = df.groupby(pd.Grouper(freq='AS')).idxmin()
        return pd.value_counts([d.month for d in years_minimum["data"]]).idxmax()
    
    def hydrologic_years_dict(self,df):
        n_month = self.starting_month_hydrologic_year(df)
        gp = df["data"].groupby(pd.Grouper(freq="AS-%s"%meses[n_month]))
        dic = dict(list(gp))
        annual_dic={key:dic[key] for key in dic.keys()}
        '''        for key in dic.keys():
            df_year=pd.DataFrame({'data':dic[key].values,'hyear':[key for i in dic[key].index]},index=dic[key].index)
            hydrologic_years.append(df_year)
        df=pd.concat(hydrologic_years)
        print(df)'''
        return annual_dic
    
    def get_reduced_serie(self,original,discretization,reduction):
        return ReducedSerie.objects.filter(
                original_serie = original,discretization=discretization,reduction=reduction)
    
    @abstractmethod
    def reduce(self):
        pass
    
    def get_graphs_data(self,daily,original,discretization):
        graph=generic_obj()
        reduceds=[]
        xys=[]
        for reduction in self.reductions:
            reduced=self.get_reduced_serie(
                original,discretization,reduction)
            if reduced:
                temporal_data = TemporalSerie.objects.filter(
                    id=reduced[0].temporal_serie_id)
                reduced=reduced[0]
                reduced.temporals=temporal_data
            else:
                date,data=self.reduce(daily,discretization,reduction)
                temporal_data,reduced=self.get_temporal_data(
                    original,discretization,reduction,data,date)
                reduced.temporals=temporal_data
            reduceds.append(reduced)
            x=[t.date for t in reduced.temporals]
            y=[t.data for t in reduced.temporals]
            xys.append([x,y])
        graph.variable=original.variable
        graph.discretization=discretization
        graph.reduceds=reduceds
        graph.xys = xys
        names=[r.type for r in self.reductions]
        return graph
    
    def get_or_create_reduced_series(self):
        self.update_originals()
        self.update_variables_and_sources()
        self.reduceds=[]
        graphs=[]
        for original in self.originals:
            temporals = TemporalSerie.objects.filter(id=original.temporal_serie_id)
            daily = self.create_daily_data_pandas(temporals)
            anos_hidrologicos = self.hydrologic_years_dict(daily)
            discretizations=self.discretizations[:]
            for discretization in discretizations:
                graph = self.get_graphs_data(daily,original,discretization)
                names=[r.type for r in self.reductions]
                graph.graph = plot_web(xys=graph.xys,
                                          title=_("%(discretization)s %(variable)s")%
                                                {'variable':str(original.variable),
                                                 'discretization':str(discretization)
                                                 },
                                            variable=original.variable,unit=original.unit,names=names)
                graphs.append(graph)
        self.reduceds = graphs
        return self.reduceds
    
    def get_temporal_data(self,original,discretization,reduction,dados,datas):
        id = criar_temporal(dados,datas)
        reduced_serie = ReducedSerie.objects.create(
                original_serie = original,
                discretization = discretization,
                reduction = reduction,
                temporal_serie_id = id
        )
        reduced_serie.save()
        return TemporalSerie.objects.filter(id=id),reduced_serie
    
class BasicStats(BaseStats):
    def reduce(self,daily,discretization,reduction):
        gp = pd.Grouper(freq=discretization.pandas_code)
        discretized = daily.groupby(gp).agg(funcoes_reducao[reduction.type_pt_br])
        date = list(discretized.index)
        data = list(discretized["data"])
        return date,data

class RollingMean(BaseStats):
    def reduce(self,daily,discretization,reduction):
        daily_rolling_mean = daily.rolling(window=int(discretization.pandas_code),center=False).mean()
        hydrologic_years = self.hydrologic_years_dict(daily_rolling_mean)
        gp = pd.Grouper(freq="10AS")
        years = sorted(list(hydrologic_years.keys())[1:])
        data = [hydrologic_years[year].groupby(gp).agg(funcoes_reducao[reduction.type_pt_br]).max()
                 for year in years if not hydrologic_years[year].groupby(gp).agg(funcoes_reducao[reduction.type_pt_br]) is (nan)]
        date = [hydrologic_years[year].groupby(gp).agg(funcoes_reducao[reduction.type_pt_br]).idxmax()
                 for year in years  if not hydrologic_years[year].groupby(gp).agg(funcoes_reducao[reduction.type_pt_br]) is (nan)]
        return date,data
    
  

class BaseAnnualEvents(BaseStats,metaclass=ABCMeta):
    
    @abstractmethod
    def get_reduced_value(self,df,reduction):
        pass
    
    def reduce(self,daily,discretization,reduction):
        hydrologic_years = self.hydrologic_years_dict(daily)
        years = sorted(list(hydrologic_years.keys())[1:])
        data = []
        for year in years:
            df = hydrologic_years[year]
            df=pd.DataFrame({'data':df.values},index=df.index)
            data.append(float(self.get_reduced_value(df,reduction)))
        date = [datetime(year.year,1,1) for year in years]
        return date,data
    

class RateOfChange(BaseAnnualEvents):
    
    def get_reduced_value(self,df,reduction):
        df['dif'] = df['data'] - df['data'].shift(1)
        return df[eval("df['dif']"+funcoes_reducao[reduction.type_en_us]+'0')]['dif'].mean()
    
    
class FrequencyOfChange(BaseAnnualEvents):
    
    def get_reduced_value(self,df,reduction):
        df['dif_unit'] = (df['data'] - df['data'].shift(1))/abs(df['data'] - df['data'].shift(1))
        events = split(df['dif_unit'], where(eval("df['dif_unit']"+funcoes_reducao[reduction.type_en_us]+"df['dif_unit'].shift(1)"))[0])
        return len(events)
    
class FrequencyOfPulses(BaseAnnualEvents):
    
    def get_reduced_value(self,df,reduction):
        df['dif_unit'] = (df['data'] - df['data'].shift(1))/abs(df['data'] - df['data'].shift(1))
        events = split(df['dif_unit'], where(eval("df['dif_unit']"+funcoes_reducao[reduction.type_en_us]+"df['dif_unit'].shift(1)"))[0])
        return len(events)
    
class DurationOfPulses(BaseAnnualEvents):
    
    def get_reduced_value(self,df,reduction):
        df['dif_unit'] = (df['data'] - df['data'].shift(1))/abs(df['data'] - df['data'].shift(1))
        events = split(df['dif_unit'], where(eval("df['dif_unit']"+funcoes_reducao[reduction.type_en_us]+"df['dif_unit'].shift(1)"))[0])
        return len(events)
    
    
class JulianDate(BaseAnnualEvents):
    
    def get_reduced_value(self,df,reduction):
        reduction_abreviations = {'maximum':'max','minimum':'min'}
        print(df.idxmax())
        print(df.idxmin())
        date_maximum = pd.DatetimeIndex(eval('df.idx%s().values'%reduction_abreviations[reduction.type_en_us]))[0]
        julian_seconds = date_maximum-datetime(date_maximum.year,1,1)
        return julian_seconds.days




    
def get_daily_data(station,variable):
    originals = OriginalSerie.objects.filter(station=station)
    originals=get_originals([variable,],originals)
    temporals = TemporalSerie.objects.filter(id=originals[0].temporal_serie_id)
    data = [o.data if not o is None else nan for o in temporals]
    date = [o.date for o in temporals]
    df = pd.DataFrame({"data" : data}, index=pd.DatetimeIndex(date))
    gp = pd.Grouper(freq='D',sort=True)
    return df.groupby(gp).mean()
    
class IHA:
    def __init__(self,station_id,other_id,variable_id=1):
        self.station = Station.objects.get(id=station_id)
        self.other = Station.objects.get(id=station_id)
        self.variable = Variable.objects.get(id=variable_id)    
        self.daily = {'pre_data':get_daily_data(self.station,self.variable),
                      'pos_data':get_daily_data(self.other,self.variable)
                     }
        
    def Group1(self):
        month_names=['January','February','March','April','May','June','July','August','September','October','November','December']
        data={}
        for type_data in self.daily:
            daily_data = self.daily[type_data]
            daily_data['month']=[o.month for o in daily_data.index]
            mean_by_month = daily_data.groupby('month').mean()
            months = [d for d in mean_by_month.index]
            data[type_data] = [round(d[0],2) for d in mean_by_month.values]
        return [Table(month_names[i],data['pre_data'][i],data['pos_data'][i]) for i in range(12)]
    
    def Group2(self):
        datas=[]
        discretizations = list(Discretization.objects.filter(stats_type__type = 'rolling mean'))
        discretizations.sort(key=lambda x:int(x.pandas_code))
        for discretization in discretizations:
            for reduction in Reduction.objects.filter(stats_type__type = 'rolling mean'):
                data_mean = {}
                for type_data in self.daily:
                    daily_data = self.daily[type_data]
                    basic_stats = RollingMean(self.station.id,self.variable.id)
                    date,data = basic_stats.reduce(daily_data,discretization,reduction)
                    data_mean[type_data]=round(sum(data)/len(data),2)
                    
                line = Table('Annual %(reduction)s %(discretization)s means' % 
                             {'reduction':reduction.type,
                              'discretization':discretization.type},
                             data_mean['pre_data'],
                             data_mean['pos_data'],
                )
                datas.append(line)
        return datas

        
        
        
        
    
    
    
'''
    

class RollingMean(BaseStats):
    def update_informations(self,discretization_code=None,reduction_id=None):
        if discretization_code is None:
            self.discretizations=Discretization.objects.all()
            self.discretizations=[d for d in self.discretizations if d.type_en_us.endswith("rolling mean")]
        else:
            self.discretizations = Discretization.objects.filter(pandas_code=discretization_code)
        if reduction_id==None:
            self.reductions =Reduction.objects.all()
        else:
            self.reductions = Reduction.objects.filter(id=reduction_id)
    def reduce(self,daily,discretization,reduction):
        daily_rolling_mean = daily.rolling(window=int(discretization.pandas_code),center=False).mean()
        hydrologic_years = self.hydrologic_years_dict(daily_rolling_mean)
        gp = pd.Grouper(freq="10AS")
        years = sorted(list(hydrologic_years.keys())[1:])
        data = [hydrologic_years[year].groupby(gp).agg(funcoes_reducao[reduction.type_pt_br]).max()
                 for year in years if not hydrologic_years[year].groupby(gp).agg(funcoes_reducao[reduction.type_pt_br]) is (nan)]
        date = [hydrologic_years[year].groupby(gp).agg(funcoes_reducao[reduction.type_pt_br]).idxmax()
                 for year in years  if not hydrologic_years[year].groupby(gp).agg(funcoes_reducao[reduction.type_pt_br]) is (nan)]
        return date,data
    
'''    
    
    
    
    
    
 
    
    
'''    
class RazaoMudanca(BaseEcoHidro):
    def atualiza_informacoes(self,variavel_id,reducao_id):
        self.discretizacao = Discretizacao.objects.get(codigo_pandas="AS")
        self.reducao = Reducao.objects.get(id=reducao_id)
        
    def prepara_serie_reduzida(self):
        temporais = SerieTemporal.objects.filter(Id=self.original.serie_temporal_id)
        diarios = self.cria_dados_diarios_pandas(temporais)
        anos_hidrologicos = self.dicionario_de_anos_hidrologicos(diarios)
        anos = sorted(list(anos_hidrologicos.keys()))
        dados = []
        for ano in anos:
            df = anos_hidrologicos[ano]
            df=pd.DataFrame({'dado':df.values},index=df.index)
            df['dif'] = df['dado'] - df['dado'].shift(1)
            r = df[df['dif']>0]['dif'].mean()
            print(r)
            dados.append(float(r))
        datas = [datetime(ano,1,1) for ano in anos]
        return self.obtem_dados_temporais(dados,datas)
    
    
class FrequenciaMudanca(BaseEcoHidro):
    def atualiza_informacoes(self,reducao_id):
        self.discretizacao = Discretizacao.objects.get(codigo_pandas="AS")
        self.reducao = Reducao.objects.get(id=reducao_id)
        
    def prepara_serie_reduzida(self):
        temporais = SerieTemporal.objects.filter(Id=self.original.serie_temporal_id)
        diarios = self.cria_dados_diarios_pandas(temporais)
        anos_hidrologicos = self.dicionario_de_anos_hidrologicos(diarios)
        anos = sorted(list(anos_hidrologicos.keys()))
        dados = []
        for ano in anos:
            df = anos_hidrologicos[ano]
            df=pd.DataFrame({'dado':df.values},index=df.index)
            df['dif_unit'] = (df['dado'] - df['dado'].shift(1))/abs(df['dado'] - df['dado'].shift(1))
            events = np.split(a['dif'], np.where(a['dif']>a['dif'].shift(1))[0])
            r = len(events)
            dados.append(float(r))
        datas = [datetime(ano,1,1) for ano in anos]
        return self.obtem_dados_temporais(dados,datas)
        
        
'''