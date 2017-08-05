#from data.models import Stats,Discretization,Unit,Variable,ConsistencyLevel
#classes = {'stats':Stats,'discretization':Discretization,'unit':Unit,'variable':Variable,'ConsistencyLevel':ConsistencyLevel}
from stations.models import Source, StationType, Localization,Coordinate
#classes = {'Source':Source, 'StationType':StationType, 'Localization':Localization,'Coordinate':Coordinate}
from stats.models import Reduction
classes = {'Reduction':Reduction}
for classe in classes:
    with open(classe+".txt",'w',encoding="utf-8") as f:
        Classe=classes[classe]
        fields = [f.name for f in Classe._meta.fields]
        for obj in Classe.objects.all():
            nomes = [str(eval('obj.%s'%f)) for f in fields]
            f.write(",".join(nomes)+"\n")