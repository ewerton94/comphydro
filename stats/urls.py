from django.conf.urls import include, url
from .views import rolling_mean,basic_stats,rate_of_change,frequency_of_change,iha

urlpatterns =(
    url(r'^rolling_mean/(?P<station_id>[^/]+)/(?P<filters>.*)$', rolling_mean, name='rolling_mean'),
    url(r'^basic_stats/(?P<station_id>[^/]+)/(?P<filters>.*)$', basic_stats, name='basic_stats'),
    url(r'^rate_of_change/(?P<station_id>[^/]+)/(?P<filters>.*)$', rate_of_change, name='rate_of_change'),
    url(r'^frequency_of_change/(?P<station_id>[^/]+)/(?P<filters>.*)$', frequency_of_change, name='frequency_of_change'),
    url(r'^iha/(?P<station_id>[^/]+)/(?P<filters>.*)$', iha, name='iha'),
)