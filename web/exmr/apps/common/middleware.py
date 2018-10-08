from django.contrib.gis.geoip2 import GeoIP2
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin 

BLOCK_LOCATIONS = ["New York"]

class LocationBlock(MiddlewareMixin):

    def process_request(self, request):
        ip = request.META['REMOTE_ADDR']
        g = GeoIP2()
        try:
            city = g.city(ip).get("city")
        except:
        	city = None
        print(city)
        if city in BLOCK_LOCATIONS: 
                return HttpResponseForbidden()
        return None

