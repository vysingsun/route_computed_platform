Raksa Platform

How to install:
1. Install docker
2. run: docker-compose up
3. Install node module in "Platform" container:\
    3.1. run: docker-compose exec platform bash\
    3.2. run: npm install // webpack directory\
    3.3. run: npm run dev\
    3.4. Start Celery: celery worker -A raksa_platform -l info


###Open route
http://localhost:8093/
#API route
/api/v1/route(osrm or graph)
/api/v2/route (waze)


###types of route:
- osrm
- graph
- waze

###request(body)
{
   	"start_point":{
        "lat":11.5042,
        "lng":104.8837
    },
    "end_point":{
        "lat":11.5435,
        "lng":104.89190
    },
    "route":"graph",
    "scan":"false",
    "weather":"normal",
    "traffic":"false"
}
