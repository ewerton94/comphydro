from django.conf.urls import include, url
from .views import stats_view

urlpatterns =(
    url(r'^(?P<stats_name>.*)/(?P<station_id>[^/]+)/(?P<filters>.*)$', stats_view, name='stats_view'),
)