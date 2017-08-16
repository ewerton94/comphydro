# Hidrologia Computacional

Este é um aplicativo criado para facilitar estudos em hidrologia, criado pelo grupo de Pesquisa Hidrologia Estatística, do Centro de Tecnologia da Universidade Federal de Alagoas (CTEC/UFAL).

### 1. Getting started

* Pré-requisitos:

```powershell

django


```

* Procedimentos de instalação:

1. Instale os pré-requisitos necessários;
2. Obtenha este diretório em seu computador;
3. No arquivo comphydro/urls.py, comente as linhas 29 à 31:
```python
urlpatterns += i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^stations/', include('stations.urls')),
    #url(r'^', include('stations.urls')),
    #url(r'^stats/', include('stats.urls')),
)
```
4. Abra a linha de comando ou terminal na pasta do projeto no seu computador e execute o comando migrate:
```powershell
python manage.py migrate

```
5. Abra o Shell do django:
```powershell
python manage.py shell
```
6. Rode o arquivo data_manager.py:
```python
from data_manager import *
```
7. Se tudo ocorrer bem, já é possível executar o projeto:
```powershell
python manage.py runserver
```





