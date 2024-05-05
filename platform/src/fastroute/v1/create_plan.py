import math

class Plans:
    
    def radians(self,degree):
        return (3.14*degree/180)
    def get_bearing(self,s_lat, s_lng, e_lat, e_lng):
        startLat = math.radians(s_lat)
        startLong = math.radians(s_lng)
        endLat = math.radians(e_lat)
        endLong = math.radians(e_lng)
        dLong = endLong - startLong
        dPhi = math.log(math.tan(endLat / 2.0 + math.pi / 4.0) / math.tan(startLat / 2.0 + math.pi / 4.0))
        if abs(dLong) > math.pi:
            if dLong > 0.0:
                dLong = -(2.0 * math.pi - dLong)
            else:
                dLong = (2.0 * math.pi + dLong)
        bearing = math.atan2(dLong, dPhi)
        return self.new_polyline(s_lat, s_lng, e_lat, e_lng,bearing)

    def new_polyline(self,s_lat, s_lng, e_lat, e_lng, bearing):
        bearing = bearing-1.57
        R = 6378.1 #Radius of the Earth
        d = 0.006 #Distance in km
        lat1 = math.radians(s_lat)
        lon1 = math.radians(s_lng)
        lat2 = math.radians(e_lat)
        lon2 = math.radians(e_lng)

        nlat1 = math.asin( math.sin(lat1)*math.cos(d/R) + math.cos(lat1)*math.sin(d/R)*math.cos(bearing))
        nlon1 = lon1 + math.atan2(math.sin(bearing)*math.sin(d/R)*math.cos(lat1), math.cos(d/R)-math.sin(lat1)*math.sin(nlat1))

        nlat2 = math.asin( math.sin(lat2)*math.cos(d/R) + math.cos(lat2)*math.sin(d/R)*math.cos(bearing))
        nlon2 = lon2 + math.atan2(math.sin(bearing)*math.sin(d/R)*math.cos(lat2), math.cos(d/R)-math.sin(lat2)*math.sin(nlat2))
        return math.degrees(nlat1),math.degrees(nlon1),math.degrees(nlat2),math.degrees(nlon2)

    def plan_polyline(self,geometries):
        datas = geometries['block']
        dis = geometries['distance']
        latitute = []
        longitute = []
        plan = []
        for i in range(0,(len(datas)-2)):
            while len(datas)>2:
                s_lat=datas[i][0]
                s_lng=datas[i][1]
                e_lat=datas[i+1][0]
                e_lng=datas[i+1][1]
                point = self.get_bearing(s_lat, s_lng, e_lat, e_lng)
                latitute.append(point[0])
                longitute.append(point[1])
                latitute.append(point[2])
                longitute.append(point[3])
                plan.append('[{},{}]'.format(point[0],point[1]))
                plan.append('[{},{}]'.format(point[2],point[3]))
                break
        for i in reversed(range(len(datas))):
            while not i < 2:
                s_lat=datas[i][0]
                s_lng=datas[i][1]
                e_lat=datas[i-1][0]
                e_lng=datas[i-1][1]
                point = self.get_bearing(s_lat, s_lng,e_lat, e_lng)
                latitute.append(point[0])
                longitute.append(point[1])
                latitute.append(point[2])
                longitute.append(point[3])
                plan.append('[{},{}]'.format(point[0],point[1]))
                plan.append('[{},{}]'.format(point[2],point[3]))
                break
        plan=','.join(plan)
        plan = '"route":{},"draw":[{}],"latitute":{},"longitute":{},"distance":{}'.format(datas,plan,latitute,longitute,dis)
        return eval('{'+plan+'}')