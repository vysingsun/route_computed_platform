from .route_v2 import RouteR
from ..models import Variable
from ..v1.scan_driver import ScanDriver
from ..v1.insert_driver import InsertDriver

duration = 0
class RequestRouteV2: 
    route = None
    block_scan_data = []
    api_scan_driver = None
    api_route = None
    models_var = Variable()
    conditions = models_var.CONDITION
    full_route = models_var.ROUTE
    def __init__(self,s_lat, s_lng, e_lat, e_lng):
        self.conditions["start_point"]["lat"] = s_lat
        self.conditions["start_point"]["lng"] = s_lng
        self.conditions["end_point"]["lat"] = e_lat
        self.conditions["end_point"]["lng"] = e_lng

    def serve(self):
        route = RouteR(self.conditions["start_point"]["lat"],self.conditions["start_point"]["lng"],self.conditions["end_point"]["lat"],self.conditions["end_point"]["lng"])
        self.full_route["start_point"] = eval('[{},{}]'.format(self.conditions["start_point"]["lat"], self.conditions["start_point"]["lng"]))
        self.full_route["end_point"] = eval('[{},{}]'.format(self.conditions["end_point"]["lat"], self.conditions["end_point"]["lng"]))
        for name in self.conditions:
            while name is "weather":
                if not self.conditions[name] is None:
                    self.full_route["geometries"]["weather"] = self.conditions[name]
                break
        self.full_route["geometries"]["distance"] = route.get_distance()
        self.full_route["geometries"]["route"] = route.get_route()
        self.full_route["geometries"]["options"] = route.get_option()
        self.full_route["geometries"]["duration"] = route.get_duration()
        self.full_route["geometries"]["blocks_scan"] = []
        self.full_route["code"] = route.code
        return self.full_route


    def condition(self, **kwargs):
        edit = kwargs
        for name in edit:
            while not edit[name] is None:
                self.conditions[name] = edit[name]
                break
    
    def scan_route(self):
        global duration
        scan = ScanDriver()
        insert = InsertDriver()
        drivers = insert.fake()
        get = scan.scan_driver(self.api_route,drivers)
        duration = get[0]
        self.block_scan_data = get[1]
        return self.block_scan_data

            # previos version #
# from .route_v2 import RouteR
# from ..models import Variable
# duration = 0
# class RequestRouteV2: 
#     models_var = Variable()
#     conditions = models_var.CONDITION
#     full_route = models_var.ROUTE
#     def __init__(self,s_lat, s_lng, e_lat, e_lng):
#         self.conditions["start_point"]["lat"] = s_lat
#         self.conditions["start_point"]["lng"] = s_lng
#         self.conditions["end_point"]["lat"] = e_lat
#         self.conditions["end_point"]["lng"] = e_lng

#     def serve(self):
#         route = RouteR(self.conditions["start_point"]["lat"],self.conditions["start_point"]["lng"],self.conditions["end_point"]["lat"],self.conditions["end_point"]["lng"])
#         self.full_route["start_point"] = eval('[{},{}]'.format(self.conditions["start_point"]["lat"], self.conditions["start_point"]["lng"]))
#         self.full_route["end_point"] = eval('[{},{}]'.format(self.conditions["end_point"]["lat"], self.conditions["end_point"]["lng"]))
#         for name in self.conditions:
#             while name is "weather":
#                 if not self.conditions[name] is None:
#                     self.full_route["geometries"]["weather"] = self.conditions[name]
#                 break
#         self.full_route["geometries"]["distance"] = route.get_distance()
#         self.full_route["geometries"]["route"] = route.get_route()
#         self.full_route["geometries"]["options"] = route.get_option()
#         self.full_route["geometries"]["duration"] = route.get_duration()
#         self.full_route["geometries"]["blocks_scan"] = []
#         self.full_route["code"] = route.code
#         return self.full_route


#     def condition(self, **kwargs):
#         edit = kwargs
#         for name in edit:
#             while not edit[name] is None:
#                 self.conditions[name] = edit[name]
#                 break