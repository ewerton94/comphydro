import json
from data.models import Stats,Discretization,Unit,Variable,ConsistencyLevel
from stations.models import Source, StationType, Localization,Coordinate
from stats.models import Reduction
from django.db import models

classes = {'Stats':Stats,'Discretization':Discretization,'Unit':Unit,'Variable':Variable,'ConsistencyLevel':ConsistencyLevel,'Source':Source, 'StationType':StationType, 'Coordinate':Coordinate, 'Localization':Localization,'Reduction':Reduction}


'''

#Código utilizado caso queira exportar os dados do seu banco de dados:
dics={}

for classe in classes:
    dic={}
    Classe = classes[classe]
    dics[classe]={}
    fields = [f for f in Classe._meta.fields]
    dics[classe]['fields']=[]
    for obj in Classe.objects.all():
        fs={}
        for f in fields:
            if f.name!='id':
                if isinstance(f,models.ForeignKey):
                    fs["%s_id"%f.name] = eval('obj.%s.id'%f.name)
                else:
                    fs[f.name]=eval('obj.%s'%f.name)
        dics[classe]['fields'].append(fs)

with open('data.json', 'w') as outfile:
    json.dump(dics, outfile)
    
'''

with open('data.json') as infile:
    file = infile.read()
    dics = json.loads(file)

for classe in dics:
    classes[classe].objects.bulk_create([
        classes[classe](**obj) for obj in dics[classe]['fields']  
    ])


