import requests
from django.conf import settings
from ..models import Variable
class RouteR:
    coordinates = None
    steps = None
    options = []
    # value
    distance = 0
    old_time = 0
    #setting
    models = Variable()
    conditions = models.CONDITION
    VERSION_WAZE = settings.VERSION_WAZE
    def __init__(self,s_lat, s_lng, e_lat, e_lng):
        self.set_request(s_lat, s_lng, e_lat, e_lng)

    def set_request(self,s_lat, s_lng, e_lat, e_lng):
        # get data not have traffic include
        hosts = self.models.getWazData(s_lat, s_lng, e_lat, e_lng)
        if hosts == {"error": "Internal Error"}:
            self.full_route = {"code":400,"error":"Waze can not handle"}
            self.duration = 0
            self.options = []
            self.distance = 0
            self.code = 419
        else:
            self.code = 200
            self.duration = hosts['response']['totalRouteTime']
            coord = hosts['coords']
            response = hosts['response']['results']
            street = hosts['response']['streetNames']
            route = []
            for latlng in coord:
                coor = eval('['+'{},{}'.format(latlng['y'], latlng['x'])+']')
                route.append(coor)
            dis = 0
            for path in response:
                distance = path['distance']
                old = distance-dis
                dis = dis + old
                while not path['instruction'] is None:
                    direction = path['instruction']['opcode']
                    roadType = path['street']
                    streetNames = street[roadType]
                    self.options.append(eval("{" + '"point":[{},{}],"distance":{},"direction":"{}","streetName":"{}"'.format( path['path']['y'], path['path']['x'], distance, direction, streetNames) + '}'))
                    break
            self.distance = dis
            self.full_route = route

    def condition(self,**kwargs):
        edit = kwargs
        # for name in edit:
        for name in edit:
            while not edit[name] is None:
                self.conditions[name]=edit[name]
                break
        print("me",self.conditions)

    def get_route(self):
        return self.full_route

    def get_option(self):
        return self.options

    def get_distance(self):
        return self.distance

    def get_duration(self):
        return self.duration

#5341.9