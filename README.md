# Hidrologia Computacional

Este é um aplicativo criado para facilitar estudos em hidrologia, criado pelo grupo de Pesquisa Hidrologia Estatística, do Centro de Tecnologia da Universidade Federal de Alagoas (CTEC/UFAL).

### 1. Getting started

* Pré-requisitos:

```powershell

django
django-modeltranslation
pandas
bs4
psycopg2
furl
plotly
xlrd


```

* Procedimentos de instalação:

1. Instale e configure o postgresql;
2. Obtenha este diretório em seu computador;
3. Instale os pré-requisitos necessários;
* Você pode instalar executando o arquivo install_requeriments.bat no windows ou executando no terminal do linux o seguinte comando:

```terminal
python -m pip install -r requirements.txt
```
4. No arquivo comphydro/urls.py, comente as linhas 29 à 31:
```python
urlpatterns += i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^stations/', include('stations.urls')),
    #url(r'^', include('stations.urls')),
    #url(r'^stats/', include('stats.urls')),
)
```
5. Abra a linha de comando ou terminal na pasta do projeto no seu computador e execute o comando migrate (obs.: lembre-se de instalar o postgresql e criar um banco de dados com o nome comphydro):
```powershell
python manage.py migrate

```
6. Abra o Shell do django:
```powershell
python manage.py shell
```
7. Rode o arquivo data_manager.py:
```python
from data_manager import *
```
8. Descomente as linhas comentadas no ítem 3.
9. Se tudo ocorrer bem, já é possível executar o projeto:
```powershell
python manage.py runserver
```
