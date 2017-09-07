from django.conf.urls import include, url
from .views import rolling_mean,basic_stats,rate_of_change,frequency_of_change,iha,julian_date,pulse_count,pulse_duration,reference_flow

urlpatterns =(
    url(r'^rolling_mean/(?P<station_id>[^/]+)/(?P<filters>.*)$', rolling_mean, name='rolling_mean'),
    url(r'^basic_stats/(?P<station_id>[^/]+)/(?P<filters>.*)$', basic_stats, name='basic_stats'),
    url(r'^basic_stats2/(?P<station_id>[^/]+)(/discretization=(?P<price_min>\d+))?/$', basic_stats, name='basic_stats'),
    url(r'^rate_of_change/(?P<station_id>[^/]+)/(?P<filters>.*)$', rate_of_change, name='rate_of_change'),
    url(r'^frequency_of_change/(?P<station_id>[^/]+)/(?P<filters>.*)$', frequency_of_change, name='frequency_of_change'),
    url(r'^julian_date/(?P<station_id>[^/]+)/(?P<filters>.*)$', julian_date, name='julian_date'),
    url(r'^iha/(?P<station_id>[^/]+)/(?P<other_id>[^/]+)/(?P<filters>.*)$', iha, name='iha'),
    url(r'^pulse_count/(?P<station_id>[^/]+)/(?P<filters>.*)$', pulse_count, name='pulse_count'),
    url(r'^pulse_duration/(?P<station_id>[^/]+)/(?P<filters>.*)$', pulse_duration, name='pulse_duration'),
    url(r'^reference_flow/(?P<station_id>[^/]+)/(?P<filters>.*)$', reference_flow, name='reference_flow'),
)