import xlrd
import psycopg2
import matplotlib.pyplot as plt
import pandas as pd
#------------------------------------------------------------------------------
class banco():
    """adicionará os dados no banco"""
    def __init__(self, nome_db):
        self.nome_db=nome_db

    def add_db(self, matriz, curse, ano):
        """insere dados um a um de forma automatica e organizada no 
        banco de dados e retorna e 3 listas, uma contendo a media anual, 
        outra contendo os dados daquele ano, outra os dias daquele ano"""
        dados=[]
        dias=0
        somas=[]
        for j in range(1,13):
            soma=0
            for i in matriz:
                if i[j]!='': #caso o dia existir naquele mês, isto é acionado
                    curse.execute("INSERT INTO dados (data, valor) VALUES (%s,%s)",("%d/%d"%(j,ano), i[j])) #insere no banco de dados
                    dados.append(i[j]) #insere o elemento na lista de dados
                    soma+=i[j] #somatorio para depois calcular a media anual
                    dias+=1 #somatorio de dias do ano
                else: #Caso o dia não existir naquele mês, isto é acionado
                    continue #Faz com que este dia seja ignorado
            somas.append(soma)
        media=0
        for s in somas:
            media+=s
        media=media/dias
        return (media, dados,dias)
    
    def add(self):
        """Add e guarda os dados no banco"""
        conn=psycopg2.connect(host='localhost',user='admin_db',password='pibic01',dbname='test_db')   #Conecta com o DB
        curse=conn.cursor() #Cria um cursor para manipular o DB
        curse.execute("CREATE TABLE dados (id serial PRIMARY KEY, data text, valor integer);")
        dados=[]
        media=[]
        dia=[]
        dias=0
        
        for linha in xlread(self.nome_db):
            try:    
                if ("ANO" in linha[0]):
                    ano=int(linha[0][-4:])
            except (TypeError):
                ano=ano
            if linha[0] in range(1,32):
                if linha[0]==1:
                    aux=[]
                    aux.append(linha)
                elif linha[0]==31:
                    aux.append(linha)
                    m,x,d=banco.add_db(self, aux, curse, ano)
                    media.append(m)
                    dias+=d
                    dia.append(dias)
                    for i in x:
                        dados.append(i)
                    
                else:
                    aux.append(linha)
        conn.commit()
        curse.close()
        print("\n--------------------------------------\nBanco de dados adicionado com Sucesso.\n--------------------------------------\n")
        return (media,dados, dia)
#------------------------------------------------------------------------------       
class grafico():
    #Imprimirá os graficos
    def __init__(self, dados,media_anual,dia):
        
        self.dados=dados
        self.media_anual=media_anual
        self.dia=dia
    def plot_linha(self):
        #Constroi os graficos
        x=[]
        auxiliar=0
        for i in self.dia:
            x.append(i-(i-auxiliar)/2) #alinhamento da media
            auxiliar=i
            
        plt.plot(self.dados, linewidth=1)#constroi o grafico dos dados diarios
        plt.plot(x, self.media_anual, 'k--', color='orange')#constroi o grafico das medias anuais
        plt.title("Dados diarios e Media Anual", fontsize=18)#Dá um titulo ao grafico
        plt.xlabel("Tempo em dias", fontsize=14)#Dá um titulo ao eixo x
        plt.ylabel("Valor", fontsize=14)#Dá um titulo ao eixo y
        plt.tick_params(axis='both', labelsize=14)#
        plt.grid(True)#Traça quadriculos no grafico para melhor observação
        plt.show()#Finaliza e mostra o grafico
        
    def plot_hist(self):
        #Constroi o grafico em barras das medias anuais
        x=range(len(self.dia))
        plt.bar(x, self.media_anual, width=1)
        plt.title("Media anual", fontsize=18)
        plt.xlabel("Tempo em anos", fontsize=14)
        plt.ylabel("Valor", fontsize=14)
        plt.tick_params(axis='both', labelsize=14)
    
    def plot_linha_mes(self):
        #Constroi o grafico em linha das medias mensais de cada ano
        objeto=analise_dados()
        media_mensal, mes_unico=objeto.media_mes()
        
        for i in range(0,len(mes_unico),12):
            x=[]
            for j in range(i, i+12):
                x.append(media_mensal[j])
            plt.plot(range(1,13),x,linewidth=2)
        plt.title("Media Mensal",fontsize=18)
        plt.xlabel("Meses",fontsize=14)
        plt.ylabel("Valor",fontsize=14)
        plt.grid(True)
        plt.show()
            
    
    def mostrar(self):
        #Plota os graficos
        plt.figure(1)#Plota o grafico em uma janela
        grafico.plot_linha(self)
        plt.figure(2)#Plota o segundo grafico numa segunda janela
        grafico.plot_hist(self)
        plt.figure(3)#Plota o terceiro grafico numa terceira janela
        grafico.plot_linha_mes(self)
#------------------------------------------------------------------------------
class analise_dados():
    """Conecta ao banco de dados para utilizar dos dados para construção de 
    uma lista contendo os meses dos anos e outra lista contendo a media de cada mês"""
    def connect_db(self):
        #Conecta ao banco e constroi um dicionario
        conn=psycopg2.connect(host='localhost',user='admin_db',password='pibic01',dbname='defluencia_db')   #Conecta com o DB
        curse=conn.cursor() #Cria um cursor para manipular o DB
        curse.execute("SELECT data, valor FROM dados ORDER BY id;")
        datas=curse.fetchall()
        
        mes_ano=[]
        valores=[]
        for d in datas:
            mes_ano.append(d[0])
            valores.append(d[1])
        dicionario={'data':mes_ano,'valor':valores}

        return (mes_ano, valores, dicionario)
    
    def media_mes(self):
        #Constroi um dataframe com o dicionario criado para melhor uso de dados
        mes_ano, valores, dicionario=analise_dados.connect_db(self)
        dataF=pd.DataFrame(dicionario)
        
        dataF.to_json('defluencia_db.json') #Salva o banco de dados em .json
        dataF.to_excel('defluencia_db.xls')
        
        mes_unico=[]
        for item in mes_ano:
            if not item in mes_unico:
                mes_unico.append(item)
        media_mensal=[]
        for i in mes_unico:
            media_mensal.append(float("%f"% dataF[dataF.data == '%s' %i].mean()))
        return (media_mensal, mes_unico)
#------------------------------------------------------------------------------
def xlread(arq_xls):
    """Função que ler arquivos .xls"""
    xls = xlrd.open_workbook(arq_xls)
    plan = xls.sheets()[0]
    
    for i in range(plan.nrows):
        yield plan.row_values(i)

#MAIN--------------------------------------------------------------------------
nome_db=input("Qual o nome do arquivo .xls que está o banco de dados?\n")
db=banco(nome_db)#cria um obejto utilizando do nome do arquivo excel
media,dados,dia=db.add()

b=analise_dados()
media_mensal, mes_unico=b.media_mes()

figura=grafico(dados,media,dia)
