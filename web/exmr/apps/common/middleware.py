from django.contrib.gis.geoip2 import GeoIP2
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin 

BLOCK_REGION = ["NY"]

class LocationBlock(MiddlewareMixin):

    def process_request(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        g = GeoIP2()
        try:
            city = g.city(ip)["region"]
            print(g.city(ip))
        except:
        	city = None
        print(city)
        if city in BLOCK_REGION: 
                return HttpResponseForbidden()
        return None

