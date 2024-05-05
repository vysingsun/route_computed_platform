from time import strftime, gmtime
import requests,json
from django.shortcuts import render
# Create your views here
from .v1.requests_route import RequestRoute

# re = RequestRoute(str(11.584637323468067),str(104.90419534099364),str(11.590755565413504),str(104.90661149727481))
# re.condition(scan="true",weather="storming",route="osrm")# true , false(default)"
# data = re.serve()
# print("my data: ", data)
class CurrentView:
    def index(request):
        response = requests.get('http://api.ipstack.com/103.216.51.117?access_key=c3ae01b20017a4dc59fa423101f5fe05')
        geodata = response.json()
        context = {
            'ip': geodata['ip'],
            'country': geodata['country_name'],
            'latitude': geodata.get('latitude', ''),
            'longitude': geodata.get('longitude', ''),
        }
        return render(request, 'fastroute/home.html', context)
    # use but not work with lat long
    async def google_map():
        response = RequestRoute.get_route_data()
        gcoor = [{'lat': point[0], 'lng': point[1]} for point in response['geometries']['route']]
        context = {
            'model': "Bike",
            'distance': response['geometries']['distance'] / 1000,
            'duration': strftime("%Hh:%Mm:%Ss", gmtime(response['geometries']['duration'])),
            'map': gcoor,
            'lat_s': response['start_point']['lat'],
            'lng_s': response['start_point']['lng'],
            'lat_e': response['end_point']['lat'],
            'lng_e': response['end_point']['lng'],
            'data_delay': response['geometries']['blocks_scan'],
        }
        return render_template("fastroute/success_drawing.html", context=context)


    # use to draw map
    def open_street_map(request):
        # end 11.564223265091014, 104.87092948096951
        # end 12.203634, 104.664269
        # 11.981854, 104.722944
        # 11.531581, 104.827453
        # start 11.584637323468067, 104.90419534099364
        # start 11.825875, 104.797511
        # start 11.951962, 104.718364
        data = {
            "start_point": {
                "lat": 11.584637323468067,
                "lng": 104.90419534099364
            },
            "end_point": {
                "lat": 11.531581,
                "lng": 104.827453
            },
            "scan": True,
            "traffic": True,
        }
        # data = {
        #     "start_point": {
        #         "lat": 11.24234,
        #         "lng": 104.43543
        #     },
        #     "end_point": {
        #         "lat": 11.24234,
        #         "lng": 104.3432
        #     },
        #     "scan": True,
        #     "traffic": True
        # }
        # response = requests.get("http://localhost:8000/api/v2/route", json=data).json()
        response = requests.get("http://localhost:8000/api/v1/route", json=data).json()
        print("log: ",response)
        context = {
            # request
            'model': "Bike",
            'distance': response['geometries']['distance'] / 1000,
            'duration': strftime("%Hh:%Mm:%Ss", gmtime(response['geometries']['duration'])),
            'map': response['geometries']['route'],
            'lat_s': data['start_point']['lat'],
            'lng_s': data['start_point']['lng'],
            'lat_e': data['end_point']['lat'],
            'lng_e': data['end_point']['lng'],
            'data_delay': response['geometries']['blocks_scan'],
        }
        return render(request, 'fastroute/map.html', context)
