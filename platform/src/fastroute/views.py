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
    def google_map(self):
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
        response = requests.get("http://localhost:8000/api/route/waze", json=data).json()
        gcoor = []
        for i in range(len(response['geometries']['route'])):
            gcoor.append('{lat:'+str(response['geometries']['route'][i][0])+',lng:'+str(response['geometries']['route'][i][1])+'}')
        gcoor=','.join(gcoor)
        context = {
            # request
            'model': "Bike",
            'distance': response['geometries']['distance'] / 1000,
            'duration': strftime("%Hh:%Mm:%Ss", gmtime(response['geometries']['duration'])),
            'map': gcoor,
            'lat_s': data['start_point']['lat'],
            'lng_s': data['start_point']['lng'],
            'lat_e': data['end_point']['lat'],
            'lng_e': data['end_point']['lng'],
            'data_delay': response['geometries']['blocks_scan'],
        }
        return render(self,'fastroute/success_drawing.html',context)
    # use but not work with lat long

    # use to draw map
    def open_street_map(request):
        # end 11.564223265091014, 104.87092948096951
        # end 12.203634, 104.664269
        # 11.981854, 104.722944
        # 11.531581, 104.827453
        # startV1 11.584637323468067, 104.90419534099364
        # start 11.825875, 104.797511
        # start 11.951962, 104.718364
        # endV2 Point 11.593499, 104.873365
        # 3rdV3 11.598114, 104.875190
        data = {
            "start_point": {
                "lat": 11.584637323468067,
                "lng": 104.90419534099364
            },
            "end_point": {
                "lat": 11.598114,
                "lng": 104.875190
            },
            "scan": True,
            "traffic": True,
        }
        response = requests.get("http://localhost:7000/api/v1/route", json=data).json()
        # response = requests.get("http://localhost:8000/", json=data).json()
        # response = requests.get("http://localhost:8000/api/route/osrm", json=data).json()
        # print("Log: ",response)
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
    #just test draw map
    def test_api(request):
        request_start_lat = '11.5280'  # lng, lat
        request_start_lng = '104.9248'  # lng, lat
        request_end_lat = '11.5654'    # lng, lat
        request_end_lng = '104.8998'    # lng, lat
        route = ["routed-bike","routed-car"]
        response_bike = requests.get('https://routing.openstreetmap.de/'+route[0]+'/route/v1/driving/'+request_start_lng+','+request_start_lat+';'+request_end_lng+','+request_end_lat+'?overview=false&geometries=polyline&steps=true')
        response_car = requests.get('https://routing.openstreetmap.de/'+route[1]+'/route/v1/driving/'+request_start_lng+','+request_start_lat+';'+request_end_lng+','+request_end_lat+'?overview=false&geometries=polyline&steps=true')
        # response = requests.get("https://routing.openstreetmap.de/routed-car/route/v1/driving/104.8912,11.5684;104.8834,11.504?overview=false&geometries=polyline&steps=true")
        # response = requests.get("https://api.openrouteservice.org/v2/directions/cycling-road?api_key=5b3ce3597851110001cf624878418d2388b344e4a0036d25d0581bc1&start=104.883438,11.504154&end=104.891045,11.568393")
        json_data_car = response_car.json()
        json_data_bike = response_bike.json()
        response_car.close()
        response_bike.close()

        distance_car = json_data_car['routes'][0]['distance']
        duration_car = json_data_car['routes'][0]['duration']
        distance_bike = json_data_bike['routes'][0]['distance']
        duration_bike = json_data_bike['routes'][0]['duration']
        if (duration_car*4.07) <= duration_bike:
            json_data = json_data_car
            distance = distance_car/1000
            duration = strftime("%Hh:%Mm:%Ss", gmtime(duration_car))
        else:
            json_data = json_data_bike
            distance = distance_bike/1000
            duration = strftime("%Hh:%Mm:%Ss", gmtime(duration_bike))


        steps = json_data['routes'][0]['legs'][0]['steps']
        waypoints = json_data['waypoints']
        # define step routes
        start_point = json_data['waypoints'][0]
        lat_s = start_point['location'][1]
        lng_s = start_point['location'][0]
        end_point = json_data['waypoints'][1]
        lat_e = end_point['location'][1]
        lng_e = end_point['location'][0]
        new_data = []
        for step in steps:
            intersections = step['intersections']
            for intersection in intersections:
                locations = intersection['location']
                for x in range(0,1):
                    lng=locations[0]
                    lat=locations[1]
                new_data.append('{lat:'+str(lat)+',lng:'+str(lng)+'}')
        fullStr = ','.join(new_data) # convert list to string
        # new_data = a+fullStr+b #new data is a string
        new_data = fullStr
        # print(new_data)

        # offer data
    # >>>>>>> d78d56b7d0ed6c9313be0806769fcc64725038d2
        context={
            'distance':distance,
            'duration':duration,
            # 'dicrect':way_route,
            'map':new_data,
            'lat_s':lat_s,
            'lng_s':lng_s,
            'lat_e':lat_e,
            'lng_e':lng_e,
        }
        return render(request, 'fastroute/success_drawing.html',context)
    
    # use to draw map  from fastapi
    def open_street_map_fastapi(request):
        # data = {
        #     "start_point": {
        #         "lat": 11.584637323468067,
        #         "lng": 104.90419534099364
        #     },
        #     "end_point": {
        #         "lat": 11.567172,
        #         "lng": 104.900340
        #     },
        #     "rd_point": {
        #         "lat": 11.560297,
        #         "lng": 104.907557
        #     },
        #     "scan": True,
        #     "traffic": True,
        # }
        data = {
            "start_point": {
                "lat": 11.584637323468067,
                "lng": 104.90419534099364
            },
            "end_point": {
                "lat": 11.598114,
                "lng": 104.875190
            },
            "scan": True,
            "traffic": True,
        }
        response = requests.get("http://localhost:7000/api/v1/route", json=data).json()
        # response = requests.get("http://localhost:8000/", json=data).json()
        # response = requests.get("http://localhost:8000/api/route/osrm", json=data).json()
        # print("Log: ",response)
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
    #just test draw map
    def test_api(request):
        request_start_lat = '11.5280'  # lng, lat
        request_start_lng = '104.9248'  # lng, lat
        request_end_lat = '11.5654'    # lng, lat
        request_end_lng = '104.8998'    # lng, lat
        route = ["routed-bike","routed-car"]
        response_bike = requests.get('https://routing.openstreetmap.de/'+route[0]+'/route/v1/driving/'+request_start_lng+','+request_start_lat+';'+request_end_lng+','+request_end_lat+'?overview=false&geometries=polyline&steps=true')
        response_car = requests.get('https://routing.openstreetmap.de/'+route[1]+'/route/v1/driving/'+request_start_lng+','+request_start_lat+';'+request_end_lng+','+request_end_lat+'?overview=false&geometries=polyline&steps=true')
        # response = requests.get("https://routing.openstreetmap.de/routed-car/route/v1/driving/104.8912,11.5684;104.8834,11.504?overview=false&geometries=polyline&steps=true")
        # response = requests.get("https://api.openrouteservice.org/v2/directions/cycling-road?api_key=5b3ce3597851110001cf624878418d2388b344e4a0036d25d0581bc1&start=104.883438,11.504154&end=104.891045,11.568393")
        json_data_car = response_car.json()
        json_data_bike = response_bike.json()
        response_car.close()
        response_bike.close()

        distance_car = json_data_car['routes'][0]['distance']
        duration_car = json_data_car['routes'][0]['duration']
        distance_bike = json_data_bike['routes'][0]['distance']
        duration_bike = json_data_bike['routes'][0]['duration']
        if (duration_car*4.07) <= duration_bike:
            json_data = json_data_car
            distance = distance_car/1000
            duration = strftime("%Hh:%Mm:%Ss", gmtime(duration_car))
        else:
            json_data = json_data_bike
            distance = distance_bike/1000
            duration = strftime("%Hh:%Mm:%Ss", gmtime(duration_bike))


        steps = json_data['routes'][0]['legs'][0]['steps']
        waypoints = json_data['waypoints']
        # define step routes
        start_point = json_data['waypoints'][0]
        lat_s = start_point['location'][1]
        lng_s = start_point['location'][0]
        end_point = json_data['waypoints'][1]
        lat_e = end_point['location'][1]
        lng_e = end_point['location'][0]
        new_data = []
        for step in steps:
            intersections = step['intersections']
            for intersection in intersections:
                locations = intersection['location']
                for x in range(0,1):
                    lng=locations[0]
                    lat=locations[1]
                new_data.append('{lat:'+str(lat)+',lng:'+str(lng)+'}')
        fullStr = ','.join(new_data) # convert list to string
        # new_data = a+fullStr+b #new data is a string
        new_data = fullStr
        # print(new_data)

        # offer data
    # >>>>>>> d78d56b7d0ed6c9313be0806769fcc64725038d2
        context={
            'distance':distance,
            'duration':duration,
            # 'dicrect':way_route,
            'map':new_data,
            'lat_s':lat_s,
            'lng_s':lng_s,
            'lat_e':lat_e,
            'lng_e':lng_e,
        }
        return render(request, 'fastroute/success_drawing.html',context)
    
    # use to draw map  from fastapi
    def open_street_map_fastapi(request):
        data = {
            "start_point": {
                "lat": 11.584637323468067,
                "lng": 104.90419534099364
            },
            "end_point": {
                "lat": 11.567172,
                "lng": 104.900340
            },
            "scan": True,
            "traffic": True,
        }
        print("test")
        response = requests.get("http://localhost:7000/api/v1/route/multiplepoint", json=data).json()
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
