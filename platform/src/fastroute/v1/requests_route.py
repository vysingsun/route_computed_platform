import random, requests
from django.conf import settings
from .scan_driver import ScanDriver
from .insert_driver import InsertDriver
from  ..models import Variable
duration = 0
class RequestRoute: 
    # array
    route = None
    block_scan_data = []
    # un_know
    coordinates = None
    insert_times = None
    steps = None
    # api
    api_scan_driver = None
    api_route = None
    # value
    distance = 0
    old_time = 0
    options = None
    # selfiable in setting config
    models = Variable()
    conditions = models.CONDITION
    full_route = models.ROUTE
    def __init__(self,s_lat, s_lng, e_lat, e_lng):
        self.models.setStartLatLng(s_lat, s_lng)
        self.models.setEndLatLng(e_lat, e_lng)

    def serve(self):
        for name in self.conditions:     
            while name is "route":
                if self.conditions[name] == "osrm":
                    self.dynamic_route("osrm")
                else:
                    self.dynamic_route("graph")
                self.full_route["geometries"]["duration"] = duration
                break
            while name is "scan":
                if self.conditions[name] == True:
                    self.scan_route()
                    self.full_route["geometries"]["duration"] = duration
                    self.full_route["geometries"]["blocks_scan"] = self.block_scan_data
                else:
                    self.full_route["geometries"]["blocks_scan"] = []
                break
            # while name is "weather":
            #     if not self.conditions[name] is None:
            #         self.full_route["geometries"]["weather"] = self.conditions[name]
            #     break
        self.full_route["geometries"]["distance"] = self.distance
        self.full_route["geometries"]["route"] = self.route
        self.full_route["geometries"]["options"] = self.options
        self.full_route["start_point"] = eval('[{},{}]'.format(self.route[0][0], self.route[0][1]))
        self.full_route["end_point"] = eval('[{},{}]'.format(self.route[len(self.route) - 1][0], self.route[len(self.route) - 1][1]))
        return self.full_route

    def condition(self,**kwargs):
        edit = kwargs
        for name in edit:
            while not edit[name] is None:
                self.conditions[name]=edit[name]
                break

    def dynamic_route(self,types):
        global duration
        if types is None or types is "osrm" or types != "graph":
            # print("model", types)
            osrm_bike = requests.get('https://routing.openstreetmap.de/routed-bike/route/v1/driving/{},{};{},{}?overview=full&geometries=geojson&steps=true&generate_hints=false'.format(self.conditions["start_point"]["lng"], self.conditions["start_point"]["lat"], self.conditions["end_point"]["lng"], self.conditions["end_point"]["lat"])).json()
            duration = osrm_bike['routes'][0]['duration']
            self.distance = osrm_bike['routes'][0]['distance']
            self.old_time = osrm_bike['routes'][0]['duration']
            self.json_data = osrm_bike
            self.steps = osrm_bike['routes']
            self.coordinates = osrm_bike['routes'][0]['geometry']['coordinates']
            self.options_osrm()
        elif types is "graph":
            key = settings.KEY_GRAPH
            rand_key = random.choice(key)
            print("KEY used:",rand_key,"of <<",len(key),">> keys")
            graph_bike = requests.get('https://graphhopper.com/api/1//route?point={}%2C{}&point={}%2C{}&type=json&locale=en-US&vehicle=car&weighting=fastest&elevation=true&key={}&points_encoded=false'.format(self.conditions["start_point"]["lat"], self.conditions["start_point"]["lng"], self.conditions["end_point"]["lat"], self.conditions["end_point"]["lng"],rand_key)).json()
            duration = graph_bike['paths'][0]['time']
            self.json_data = graph_bike
            self.distance = graph_bike['paths'][0]['distance']
            self.old_time = graph_bike['paths'][0]['time']
            self.steps = graph_bike['paths']
            self.coordinates = graph_bike['paths'][0]['points']['coordinates']
            self.options_graph()
        
        if not self.coordinates is None:
            return self.get_single_map()
        else:
            return self.dynamic_route(types)

    def scan_route(self):
        global duration
        scan = ScanDriver()
        insert = InsertDriver()
        drivers = insert.fake()
        get = scan.scan_driver(self.api_route,drivers)
        duration = get[0]
        self.block_scan_data = get[1]
        return self.block_scan_data

    # setter
    def get_single_map(self):
        final_route = []
        coordinate_route = []
        lat = None
        lng = None
        for coordinate in self.coordinates:
            lng = coordinate[0]
            lat = coordinate[1]
            coordinate_route.append('[{},{}]'.format(lat, lng))
        coordinate_route = ','.join(coordinate_route)
        final_route.append('"point1":[{},{}],"point2":[{},{}],"route":[{}],"duration":{},"distance":{}'.format(self.coordinates[0][1], self.coordinates[0][0], lat, lng,coordinate_route,duration,self.distance))
        final_route = ','.join(final_route)
        self.api_route = eval('{' + final_route + '}')
        self.route = eval('['+coordinate_route+']')
        return self.route

    def get_multi_map(self):
        index_route = []
        final_route = []
        route = self.coordinates
        for i in range(0, len(self.steps)):
            road = []
            for co in route:
                coor = '[{},{}]'.format(co[1],co[0])
                road.append(coor)
            road = ','.join(road)
            index_route.append('"route":[{}],"duration":{},"distance":{}'.format(road,duration,self.distance))
        index_route = ','.join(index_route)
        final_route.append('{'+index_route+'}')
        final_route = ','.join(final_route)
        self.co_route = eval('{' + '"point1":[{},{}],"point2":[{},{}],"route":[{}]'.format(self.coordinates[0][1],self.coordinates[0][0],self.coordinates[len(self.coordinates) - 1][1],self.coordinates[len(self.coordinates) - 1][0],final_route) + '}')
        return self.co_route
    
    def options_osrm(self):
        options = []
        step = self.json_data['routes'][0]['legs'][0]['steps']
        for steps in step:
            point = eval('[{},{}]'.format(steps['maneuver']['location'][1],steps['maneuver']['location'][0]))
            distance = steps['distance']
            if not steps['name'] is "":
                streetName = steps['name']
            else:
                streetName = "None"
            if "modifier" in steps['maneuver']:
                direction = "TURN_"+steps['maneuver']['modifier'].upper()
            else:
                direction = "NONE"
            options.append(eval('{'+'"point":{},"distance":{},"direction":"{}","streetName":"{}"'.format(point,distance,direction,streetName)+'}'))
        self.options = options
        return self.options

    def options_graph(self):
        options = []
        step = self.json_data['paths'][0]['instructions']
        for instructions in  step:
            distance = instructions['distance']
            direction = instructions['text']
            streetName = instructions['street_name']
            while streetName is "":
                streetName = "None"
                break
            options.append(eval('{'+'"point":None,"distance":{},"direction":"{}","streetName":"{}"'.format(distance,direction,streetName)+'}'))
        self.options = options
        return self.options
