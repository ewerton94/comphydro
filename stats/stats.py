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
        originals=[]
        for variable in self.variables:
            originals_by_variable=[o for o in self.originals if o.variable==variable]
            id_data_type = 2 if 2 in [o.consistency_level.id for o in originals_by_variable] else 1
            originals.append([o for o in originals_by_variable if o.consistency_level.id == id_data_type][0])
        self.originals=originals
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
    
    
class RateOfChange(BaseStats):
        
    def reduce(self,daily,discretization,reduction):
        hydrologic_years = self.hydrologic_years_dict(daily)
        years = sorted(list(hydrologic_years.keys())[1:])
        data = []
        for year in years:
            df = hydrologic_years[year]
            df=pd.DataFrame({'data':df.values},index=df.index)
            df['dif'] = df['data'] - df['data'].shift(1)
            r = df[eval("df['dif']"+funcoes_reducao[reduction.type_en_us]+'0')]['dif'].mean()
            data.append(float(r))
        date = [datetime(year.year,1,1) for year in years]
        return date,data
    
class FrequencyOfChange(BaseStats):    
    def reduce(self,daily,discretization,reduction):
        hydrologic_years = self.hydrologic_years_dict(daily)
        years = sorted(list(hydrologic_years.keys())[1:])
        data = []
        for year in years:
            df = hydrologic_years[year]
            df=pd.DataFrame({'data':df.values},index=df.index)
            df['dif_unit'] = (df['data'] - df['data'].shift(1))/abs(df['data'] - df['data'].shift(1))
            events = split(df['dif_unit'], where(eval("df['dif_unit']"+funcoes_reducao[reduction.type_en_us]+"df['dif_unit'].shift(1)"))[0])
            print(events)
            r = len(events)
            data.append(float(r))

        date = [datetime(year.year,1,1) for year in years]
        return date,data
    
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