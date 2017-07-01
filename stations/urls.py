from django.conf.urls import include, url
from .views import create_station,stations,station_information

urlpatterns =(
    url(r'^new$', create_station,name="create_station"),
    url(r'^$', stations,name="stations"),
    url(r'^(?P<station_id>[^/]+)/information/(?P<filters>.*)$', station_information,name="station_information"),
)