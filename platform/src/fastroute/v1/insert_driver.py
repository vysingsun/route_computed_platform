import random

class InsertDriver:
    array_driver = []
    def driver(self,lat,lng,speed):
        return self.array_driver.append(eval('['+str(lat)+','+str(lng)+','+str(speed)+']'))

    def fake(self):
        num_driver = random.randrange(5000, 10000)
        for i in range(num_driver):
            add = random.randrange(0,99999999)
            lat = '11.'+str(add)
            add = random.randrange(0,99999999)
            lng = '104.'+str(add)
            self.driver(lat,lng, random.randrange(0,65))
        
        # print(self.array_driver)
        return self.array_driver
        # self.array_driver=','.join(self.array_driver)
        # print("Driver",self.array_driver)
        driver = '['+self.array_driver+']'
        return eval(driver)