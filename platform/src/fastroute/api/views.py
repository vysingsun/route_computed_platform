from rest_framework import generics
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from ..models import RouteTest
from .serializers import RouteSerializer
from ..v1.requests_route import RequestRoute
from ..v2.requests_route_v2 import RequestRouteV2
from ..models import Variable
class RouteViewTest(generics.CreateAPIView):
    serializer_class = RouteSerializer
    queryset = RouteTest.objects.all()

    def post(self, request, lat=None, long=None, *args, **kwargs):
        # print(lat)
        # print(long)
        return super().post(request, *args, **kwargs)

class RouteView(ModelViewSet):
    direction = None
    route = None
    def get_route_osrm_grab(self, request, **kwargs):
        models_var = Variable()
        condition = models_var.CONDITION
        for name in condition:
            while name is "end_point":
                if request.data.get(name) is None or request.data.get(name) == []:
                    condition[name] = []
                    
                    return Response(models_var.ROUTE429)
                else:
                    condition[name] = request.data.get(name)
                    
                break
            while not request.data.get(name) is None:
                condition[name] = request.data.get(name)
                
                break
    
        while not condition['end_point'] is (None or []):
            do = RequestRoute(str(condition['start_point']['lat']),str(condition['start_point']['lng']),str(condition['end_point']['lat']),str(condition['end_point']['lng']))
            do.condition(route=condition['route'])# osrm(default) , graph
            # do.condition(scan=condition['scan'])# true , false(default)"
            # do.condition(weather=condition['weather'])# true , false(default)
            print("DO: ",do.serve())
            return Response(do.serve())

    def get_route_waze(self,request, **kwargs):
        models_var = Variable()
        condition = models_var.CONDITION
        print("My Condition: ", condition)
        for name in condition:
            while name is "end_point":
                if request.data.get(name) is None or request.data.get(name)==[]:
                    condition[name] = []
                    return Response(models_var.ROUTE429)
                else:
                    condition[name] = request.data.get(name)
                break
            while not request.data.get(name) is None:
                condition[name] = request.data.get(name)
                break

        while not condition['end_point'] is (None or []):
            # dov2 = RequestRouteV2(str(condition['start_point']['lat']),str(condition['start_point']['lng']),str(condition['end_point']['lat']),str(condition['end_point']['lng']))
            dov2 = RequestRouteV2(str(condition['start_point']['lat']),str(condition['start_point']['lng']),str(condition['end_point']['lat']),str(condition['end_point']['lng']))
            # dov2.condition(weather=condition['weather'])  # true , false(default)
            dov2.condition(route=condition['route'])
            dov2.condition(scan=condition['scan'])# true , false(default)"
            # dov2.condition(traffic=condition['traffic'])  # true , false(default)
            # print(models_var.CONDITION)
            return Response(dov2.serve())
        
    def get_route_multiple_point_osrm_grab(self, request, **kwargs):
        models_var = Variable()
        condition = models_var.CONDITION
        for name in condition:
            while name is "end_point":
                if request.data.get(name) is None or request.data.get(name) == []:
                    condition[name] = []
                    
                    return Response(models_var.ROUTE429)
                else:
                    condition[name] = request.data.get(name)
                    
                break
            while not request.data.get(name) is None:
                condition[name] = request.data.get(name)
                
                break
    
        while not condition['end_point'] is (None or []):
            do = RequestRoute(str(condition['start_point']['lat']),str(condition['start_point']['lng']),str(condition['end_point']['lat']),str(condition['end_point']['lng']))
            do.condition(route=condition['route'])# osrm(default) , graph
            # do.condition(scan=condition['scan'])# true , false(default)"
            # do.condition(weather=condition['weather'])# true , false(default)
            return Response(do.serve_of_multiple_point())


# status 429 = unkwon
# status 200 = ok