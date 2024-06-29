import random, requests, json
from django.conf import settings
from .scan_driver import ScanDriver
from .insert_driver import InsertDriver
from  ..models import Variable
from itertools import permutations
import threading
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
    routes = []
    distance_route = []
    start_route = 0
    default_start = ()
    def __init__(self,s_lat, s_lng, e_lat, e_lng):
        self.models.setStartLatLng(s_lat, s_lng)
        self.models.setEndLatLng(e_lat, e_lng)
    points = [
        (11.584637323468067, 104.90419534099364),  # start_point
        (11.567172, 104.900340),  # nd_point
        (11.583854, 104.909404), # rd_point
        # (11.553859, 104.895052),   # th_point
        (11.579015, 104.917060)
    ]
    def serve(self):
        route = [[104.904165, 11.584554], [104.904779, 11.584342], [104.904747, 11.584256], [104.906104, 11.58379], [104.906492, 11.583657], [104.906569, 11.583631], [104.906649, 11.583603], [104.907089, 11.583453], [104.907232, 11.58341], [104.907312, 11.583393], [104.907358, 11.583386], [104.907412, 11.583381], [104.907465, 11.583379], [104.907519, 
11.583379], [104.907598, 11.583389], [104.907695, 11.583406], [104.90773, 11.583415], [104.908163, 11.583532], [104.909081, 11.583788], [104.909246, 11.583833], [104.909315, 11.583852], [104.909398, 11.583875]]
        for name in self.conditions:     
            while name == "route":
                if self.conditions[name] == "osrm":
                    self.dynamic_route("osrm")
                else:
                    self.dynamic_route("graph")
                break
            while name == "scan":
                if self.conditions[name] == True:
                    self.scan_route()
                    
                    self.full_route["geometries"]["blocks_scan"] = self.block_scan_data
                else:
                    self.full_route["geometries"]["blocks_scan"] = []
                break
        self.full_route["geometries"]["distance"] = self.distance
        arr_route = [[i[1],i[0]] for i in route]
        self.full_route["geometries"]["route"] = arr_route
        # self.full_route["geometries"]["route"] = self.route
        self.full_route["geometries"]["options"] = self.options
        # self.full_route["start_point"] = eval('[{},{}]'.format(self.route[0][0], self.route[0][1]))
        # self.full_route["end_point"] = eval('[{},{}]'.format(self.route[len(self.route) - 1][0], self.route[len(self.route) - 1][1]))
        print("From return serve: " , self.full_route)
        print("<=================================>")
        # print("MY ROUTE: ", self.full_route["code"])
        return self.full_route

    def condition(self,**kwargs):
        edit = kwargs
        for name in edit:
            while not edit[name] is None:
                self.conditions[name]=edit[name]
                break

    def dynamic_route(self,types):
        global duration
        if types is None or types == "osrm" or types != "graph":
            osrm_bike = requests.get('https://routing.openstreetmap.de/routed-bike/route/v1/driving/{},{};{},{}?overview=full&geometries=geojson&steps=true&generate_hints=false'.format(self.conditions["start_point"]["lng"], self.conditions["start_point"]["lat"], self.conditions["end_point"]["lng"], self.conditions["end_point"]["lat"])).json()
            # osrm_bike = requests.get('https://routing.openstreetmap.de/routed-bike/route/v1/driving/{},{};{},{};{},{}?overview=full&geometries=geojson&steps=true&generate_hints=false'.format(self.conditions["start_point"]["lng"], self.conditions["start_point"]["lat"], self.conditions["end_point"]["lng"], self.conditions["end_point"]["lat"], self.conditions["rd_point"]["lng"], self.conditions["rd_point"]["lat"])).json()
            # print("After url: ", osrm_bike)
            duration = osrm_bike['routes'][0]['duration']
            self.distance = osrm_bike['routes'][0]['distance']
            self.old_time = osrm_bike['routes'][0]['duration']
            self.json_data = osrm_bike
            self.steps = osrm_bike['routes']
            self.coordinates = osrm_bike['routes'][0]['geometry']['coordinates']
            self.options_osrm()
        elif types == "graph":
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
            if not steps['name'] == "":
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
            while streetName == "":
                streetName = "None"
                break
            options.append(eval('{'+'"point":None,"distance":{},"direction":"{}","streetName":"{}"'.format(distance,direction,streetName)+'}'))
        self.options = options
        return self.options

    def serve_of_multiple_point(self):
        print("Use test!!")
        for name in self.conditions:     
            while name == "route":
                if self.conditions[name] == "osrm":
                    route = self.dynamic_route_of_multiple_point("osrm")
                break
            while name == "scan":
                if self.conditions[name] == True:
                    self.scan_route()
                    self.full_route["geometries"]["blocks_scan"] = self.block_scan_data
                else:
                    self.full_route["geometries"]["blocks_scan"] = []
                break
        re_route = [[i[1],i[0]] for i in route]
        self.full_route["geometries"]["route"] = re_route
        return self.full_route
    
    def get_short_dis(self, start, points):
        # self.routes = []
        self.start_route = self.start_route+1
        points = [i for i in points if i != start]
        short_point = []
        shortest_distance = float('inf')

        self.conditions["start_point"] = {
            "lat": start[0],
            "lng": start[1],
        }
        
        #Add threading
        
        threads = []
        results = []
        results_lock = threading.Lock()
        
        def worker(data, index):
            self.conditions["end_point"] = {
                "lat": data[0],
                "lng": data[1],
            }
            self.dynamic_route(types='osrm')
            with results_lock:
                results.append((self.distance, data, index, self.coordinates))
        for i, data in enumerate(points):
            thread = threading.Thread(target=worker, args=(data, i))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Test Sort results by distance
        results.sort(key=lambda x: x[0])
        
        for distance, data, index, coords in results:
            print("==>: ",distance, index)
            if distance < shortest_distance:
                shortest_distance = distance
                short_point = data
                
                self.conditions["start_point"] = {
                    "lat": data[0],
                    "lng": data[1],
                }
                if self.routes != self.coordinates:
                    self.routes = self.routes+coords
      
        if len(points) > 0 :
            self.get_short_dis(short_point, points)
        return self.routes
    
    def dynamic_route_of_multiple_point(self, types=None):
        # print("CALL")
        if types is None or types == "osrm" or types != "graph":
            # Initialize the shortest distance to a large value
            shortest_distance = float('inf')
            best_route = None
            # Fixed starting point
            start_point = self.points[0]
            other_points = self.points[1:]
            
            return self.get_short_dis(start_point, other_points)
            # Iterate through all permutations of the points to find the shortest route
            # for perm in permutations(other_points):
            #     print("CALL")
            #     route = ["routed-bike","routed-car"]
            #     all_points = [start_point] + list(perm)
            #     coords = ";".join(url = f'https://routing.openstreetmap.de/{route[1]}/route/v1/driving/{coords}?overview=full&geometries=geojson&steps=true&generate_hints=false'
            #     response = requests.get(url).json()[f"{lng},{lat}" for lat, lng in all_points])
                

            #     # Get the distance for the current route
            #     distance = response['routes'][0]['distance']
            #     print("DIS: ", distance)
            #     # Check if this route is shorter than the previously found shortest route
            #     if distance < shortest_distance:
            #         shortest_distance = distance
            #         best_route = response['routes'][0]['geometry']['coordinates']

            # # Store the coordinates of the best route
            # self.coordinates = best_route

        # if self.coordinates is not None:
        #     return self.get_single_map()
        # else:
        #     return self.dynamic_route_of_multiple_points(types)
        
    # def dynamic_route_of_multiple_point(self,types):
    #     # data = {
    #     #     "nd_point": {
    #     #         "lat": 11.567172,
    #     #         "lng": 104.900340
    #     #     },
    #     #     "rd_point": {
    #     #         "lat": 11.560297,
    #     #         "lng": 104.907557
    #     #     },
    #     #     "th_point": {
    #     #         "lat": 11.562168,
    #     #         "lng": 104.919491
    #     #     },
    #     # }
        
    #     data = {
    #         "nd_point": {
    #             "lat": 11.567172,
    #             "lng": 104.900340
    #         },
    #         "rd_point": {
    #             "lat": 11.583846,
    #             "lng": 104.909445
    #         },
    #         "th_point": {
    #             "lat": 11.553859,
    #             "lng": 104.895052
    #         },
    #     }
    #     global duration
    #     if types is None or types == "osrm" or types != "graph":
            
    #         #V1
    #         osrm_bike = requests.get('https://routing.openstreetmap.de/routed-bike/route/v1/driving/{},{};{},{}?overview=full&geometries=geojson&steps=true&generate_hints=false'.format(self.conditions["start_point"]["lng"], self.conditions["start_point"]["lat"], self.conditions["end_point"]["lng"], self.conditions["end_point"]["lat"])).json()
    #         # osrm_bike = requests.get('https://routing.openstreetmap.de/routed-bike/route/v1/driving/{},{};{},{};{},{}?overview=full&geometries=geojson&steps=true&generate_hints=false'.format(self.conditions["start_point"]["lng"], self.conditions["start_point"]["lat"], self.conditions["end_point"]["lng"], self.conditions["end_point"]["lat"], self.conditions["rd_point"]["lng"], self.conditions["rd_point"]["lat"])).json()
    #         # osrm_bike_rd = requests.get('https://routing.openstreetmap.de/routed-bike/route/v1/driving/104.900340,11.567172;104.907557,11.560297?overview=full&geometries=geojson&steps=true&generate_hints=false').json()
    #         osrm_bike_rd = requests.get('https://routing.openstreetmap.de/routed-bike/route/v1/driving/{},{};{},{}?overview=full&geometries=geojson&steps=true&generate_hints=false'.format(self.conditions["start_point"]["lng"], self.conditions["start_point"]["lat"], data["rd_point"]["lng"], data["rd_point"]["lat"])).json()
            
    #         osrm_bike_th = requests.get('https://routing.openstreetmap.de/routed-bike/route/v1/driving/{},{};{},{}?overview=full&geometries=geojson&steps=true&generate_hints=false'.format(self.conditions["start_point"]["lng"], self.conditions["start_point"]["lat"], data["th_point"]["lng"], data["th_point"]["lat"])).json()
            
            
    #         self.distance = osrm_bike['routes'][0]['distance']
            
    #         self.distance_rd = osrm_bike_rd['routes'][0]['distance']

    #         self.distance_th = osrm_bike_th['routes'][0]['distance']
            
    #         print("Dis1: ",self.distance)
    #         print("Dis2: ",self.distance_rd)
    #         print("Dis3: ",self.distance_th)
            
    #         if (self.distance < self.distance_rd and self.distance < self.distance_th ):
    #             self.coordinates = osrm_bike['routes'][0]['geometry']['coordinates']
                
    #             # Send V2
    #             osrm_bike_v2_st = requests.get('https://routing.openstreetmap.de/routed-bike/route/v1/driving/{},{};{},{}?overview=full&geometries=geojson&steps=true&generate_hints=false'.format(data["nd_point"]["lng"], data["nd_point"]["lat"], data["rd_point"]["lng"], data["rd_point"]["lat"])).json()
    #             osrm_bike_v2_nd = requests.get('https://routing.openstreetmap.de/routed-bike/route/v1/driving/{},{};{},{}?overview=full&geometries=geojson&steps=true&generate_hints=false'.format(data["nd_point"]["lng"], data["nd_point"]["lat"], data["th_point"]["lng"], data["th_point"]["lat"])).json()
                
    #             self.distance_v2_st = osrm_bike_v2_st['routes'][0]['distance']
    #             self.distance_v2_nd = osrm_bike_v2_nd['routes'][0]['distance']
                
    #             # Check
    #             if (self.distance_v2_st < self.distance_v2_nd):
    #                 self.coordinates_v2 = osrm_bike_v2_st['routes'][0]['geometry']['coordinates']
    #                 self.coordinates.extend(self.coordinates_v2)
    #                 # Send V3
    #                 osrm_bike_v3 = requests.get('https://routing.openstreetmap.de/routed-bike/route/v1/driving/{},{};{},{}?overview=full&geometries=geojson&steps=true&generate_hints=false'.format(data["rd_point"]["lng"], data["rd_point"]["lat"], data["th_point"]["lng"], data["th_point"]["lat"])).json()
    #                 self.coordinates_v3 = osrm_bike_v3['routes'][0]['geometry']['coordinates']
                    
    #                 self.coordinates.extend(self.coordinates_v3)
    #         elif (self.distance_rd < self.distance and self.distance_rd < self.distance_th): 
    #             self.coordinates = osrm_bike_rd['routes'][0]['geometry']['coordinates']
                
    #             # Send V2
    #             osrm_bike_v2_st = requests.get('https://routing.openstreetmap.de/routed-bike/route/v1/driving/{},{};{},{}?overview=full&geometries=geojson&steps=true&generate_hints=false'.format(data["rd_point"]["lng"], data["rd_point"]["lat"], data["nd_point"]["lng"], data["nd_point"]["lat"])).json()
    #             osrm_bike_v2_nd = requests.get('https://routing.openstreetmap.de/routed-bike/route/v1/driving/{},{};{},{}?overview=full&geometries=geojson&steps=true&generate_hints=false'.format(data["rd_point"]["lng"], data["rd_point"]["lat"], data["th_point"]["lng"], data["th_point"]["lat"])).json()
                
    #             self.distance_v2_st = osrm_bike_v2_st['routes'][0]['distance']
    #             self.distance_v2_nd = osrm_bike_v2_nd['routes'][0]['distance']
                    
    #             if (self.distance_v2_st < self.distance_v2_nd):
    #                 self.coordinates_v2 = osrm_bike_v2_st['routes'][0]['geometry']['coordinates']
    #                 self.coordinates.extend(self.coordinates_v2)
    #                 # Send V3
    #                 osrm_bike_v3 = requests.get('https://routing.openstreetmap.de/routed-bike/route/v1/driving/{},{};{},{}?overview=full&geometries=geojson&steps=true&generate_hints=false'.format(data["nd_point"]["lng"], data["nd_point"]["lat"], data["th_point"]["lng"], data["th_point"]["lat"])).json()
    #                 self.coordinates_v3 = osrm_bike_v3['routes'][0]['geometry']['coordinates']
                    
    #                 self.coordinates.extend(self.coordinates_v3)
            
    #         # self.coordinates_rd = osrm_bike_rd['routes'][0]['geometry']['coordinates']
            
    #         # self.coordinates_th = osrm_bike_th['routes'][0]['geometry']['coordinates']
            
    #         # self.coordinates.extend(self.coordinates_rd)
            
    #         # self.coordinates.extend(self.coordinates_th)
            
    #         # print("CON: ",self.coordinates)
            
    #         # self.options_osrm()
        
    #     if not self.coordinates is None:
    #         return self.get_single_map()
    #     else:
    #         return self.dynamic_route_of_multiple_point(types)