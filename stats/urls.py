from django.conf.urls import include, url
from .views import rolling_mean,basic_stats

urlpatterns =(
    url(r'^rolling_mean/(?P<station_id>[^/]+)/(?P<filters>.*)$', rolling_mean, name='rolling_mean'),
    url(r'^basic_stats/(?P<station_id>[^/]+)/(?P<filters>.*)$', basic_stats, name='basic_stats'),
)