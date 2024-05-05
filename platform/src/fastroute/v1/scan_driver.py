import queue,math,random
from time import gmtime, strftime, process_time
import numpy as np
from django.conf import settings
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
from .create_plan import Plans

q = queue.Queue()
class ScanDriver:
    current_speed = settings.DEFAULT_SPEED
    coordinates = None
    dist = 0 # distance route
    o_dura = 0 # old duration
    def scan_driver(self,coordinates,i_driver):
        print("Start scan:",strftime("%Hh%Mmn:%Ssec", gmtime()))
        multi = self.route_and_block(coordinates)
        co_map = multi[0]  # route [lat,lng]
        block_data = multi[1]  # block
        block_data_scan = []
        driver = i_driver
        driver = []# fake in route
        for x in range(random.randrange(5000, 10000)):
            driver.append(random.choice(co_map['route']))

        j = 0
        while j < len(block_data):
            while len(block_data[j]['latitute'])>2:
                latitute = block_data[j]['latitute']
                longitute = block_data[j]['longitute']
                b_dis = block_data[j]['distance'] # distance in block
                x = np.array((longitute))
                y = np.array((latitute))
                lons_lats_vect = np.column_stack((x, y))  # Reshape coordinates
                polygon = Polygon(lons_lats_vect)  # create polygon
                drivers = []
                color = "#0000FF"# blue
                t = 0
                for i in driver:
                    point = Point(driver[t][1], driver[t][0]) # point(lng,lat)
                    while polygon.contains(point) is True:
                        drivers.append('[{},{},{}]'.format(driver[t][0], driver[t][1], random.randrange(0, 65))) #[lat,lng,speed]
                        del driver[t]
                        break
                    t = t + 1
                # end data driver
                drivers = ','.join(drivers)
                while drivers != "":
                    do = eval('[' + drivers + ']')
                    avg = 0  # average speed
                    for s in range(len(do)):
                        while len(do)>=settings.SET_NUM_DRIVER_TO_SCAN:
                            if len(do)>=settings.SET_NUM_DRIVER_TO_GET_MAX_SPEED:
                                avg = avg + do[s][2]
                            else:
                                avgs = []
                                for i in range(len(do)):
                                    avgs.append(do[i][2])
                                avg = max(avgs)
                            avg = avg / len(do)
                            avg1 = 0
                            count = 0
                            for s in range(len(do)):
                                if do[s][2]>avg:
                                    avg1 = avg1 + do[s][2]
                                    count = count+1
                            avg1 = avg1/(count+((len(do)-count)/2))
                            avg = avg1
                            # print(self.current_speed,(60.00 * self.current_speed / 100), avg)
                            # color route
                            if avg > (60.00 * self.current_speed / 100):
                                color = "#0000FF"  # blue
                            elif avg > (12.00 * self.current_speed / 100):
                                color = "#FFFF00"  # yellow
                            elif avg < (12.00 * self.current_speed / 100):
                                color = "#FF0000"  # red
                            #   distance = distance of block
                            break
                    while avg>0:
                        block_data_scan.append('{"block":' + str(block_data[j]['route']) + ',"driver":{"driving":'+str(len(do))+',"stop":'+str((len(do)-count)//2)+'},"distance":' + str(b_dis) + ',"avg_speed":' + str(avg) + ',"route_color":"' + color + '"}')
                        break
                    break
                break
            j = j + 1
        block_data_scan = ','.join(block_data_scan)
        block_data_scan = eval('['+block_data_scan+']')
        du_dis = self.update_duration(block_data_scan) # to get duration update
        print("End scan:",strftime("%Hh%Mmn:%Ssec", gmtime()))
        self.scan_driver_api = eval('{'+'"point1":{},"point2":{},"route":{},"duration":{},"distance":{},"blocks_scan":[{}]'.format(co_map['point1'],co_map['point2'],co_map['route'],du_dis,self.dist,block_data_scan)+'}')
        return du_dis, block_data_scan # duration updated, {"block"},{"block"},...
    # final update time
    def update_duration(self,traffic): # duration, distance
        global duration
        if traffic is (None or ''):
            return duration
        array_data = traffic
        i_distance = 0
        i_time = 0
        # need distance block and avg_speed, if have route new [old_time,distance]
        for index in array_data:
            dis = index['distance']
            if (dis and index['avg_speed']) != 0:
                times = dis/index['avg_speed']
                i_time = i_time + times
                i_distance = i_distance + dis
        up_duration = (self.o_dura + (i_time - i_distance / self.current_speed))
        self.insert_times = i_time
        duration = up_duration
        # print(self.o_dura,"delay:",strftime("%Hh:%Mm:%Ss", gmtime(i_time - i_distance / self.current_speed)))
        return duration

    def route_and_block(self,coordinates):
        c = Plans()
        #2 should get route from function single_map beacuse have distance to find the last block
        route = coordinates #[lat,lng]
        self.o_dura = route['duration']
        self.dist = route['distance']
        block_scan = []
        final = 0
        sum = 0
        sum2 = 0
        sum3 = 0
        coor_route = route["route"]
        for co in range(len(coor_route)):
            while co + 1 < (len(coor_route) - 1):
                slat = coor_route[co][0] #lat
                slng = coor_route[co][1] #lng
                elat = coor_route[co + 1][0]
                elng = coor_route[co + 1][1]
                coor = '[{},{}]'.format(slat,slng)
                block_scan.append(coor)
                if (sum3 - sum2) > 50:
                    dis = sum3 - sum2
                    sum2 = sum
                    # scan the block of route to send to the function scan_driver to scan driver
                    block_scan = ','.join(block_scan)
                    block_scan = eval('[{}]'.format(block_scan))
                    block_scan_dis = eval('{'+'"block":{},"distance":{}'.format(block_scan,dis) + '}')
                    q.put(c.plan_polyline(block_scan_dis))
                    block_scan = []  # reset while distance >= 50m and do with new block
                else:
                    sum3 = sum  # do until sum3 - sum2 true
                    sum = sum3 + (self.p_to_p(slat, slng, elat, elng) * 1000)
                    final = sum
                    break
            while co + 1 == len(coor_route):
                block_scan = ','.join(block_scan)
                block_scan = '[{}]'.format(block_scan)
                block_scan = eval(block_scan)
                #1 need original distance to calculate last block
                block_scan_dis = eval('{'+'"block":{},"distance":{}'.format(block_scan,(self.dist - final)) + '}')
                q.put(c.plan_polyline(block_scan_dis))
                break
        # create block ot scan driver
        full_block_data = []
        while not q.empty():
            full_block_data.append(q.get())
        # worked
        return route, full_block_data

    # distance between point to point
    def p_to_p(self, slat, slng, elat, elng):
        R = 6373.0
        lat1 = math.radians(slat)
        lon1 = math.radians(slng)
        lat2 = math.radians(elat)
        lon2 = math.radians(elng)
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return (R * c)
