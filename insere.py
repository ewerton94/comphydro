import xlrd
from visual_dados.models import Dado, Valor
def xlread(arq_xls):
    """Função que ler arquivos .xls"""
    xls = xlrd.open_workbook(arq_xls)
    plan = xls.sheets()[0]
    
    for i in range(plan.nrows):
        yield plan.row_values(i)

aux=''
arq="defluencia_db.xls"
for linha in xlread(arq):
    if linha[1]!=aux:
	obj=Dado.objects.create(data=linha[1])
	d=1
	aux=linha[1]
	data=Valor.objects.create(dado_id=obj.id, valor=linha[2],dia=d)
    else:
	if linha[2]=='':
	     d+=1
	     data=Valor.objects.create(dado_id=obj.id,valor=None, dia=d)
	else:
	     d+=1
	     data=Valor.objects.create(dado_id=obj.id, valor=linha[],dia=d)
