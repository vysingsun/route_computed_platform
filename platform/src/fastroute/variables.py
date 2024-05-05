class Variables:
    co_route = []
    conditions = {
        "start_point": [],
        "end_point": [],
        "route":"osrm",
        "weather":"normal",
        "scan":"false"
    }
    full_route = {
        "start_point": [],
        "end_point": [],
        "geometries": {
            "route":[],
            "blocks_scan": [],
            "duration": 0,
            "distance": 0,
            "weather": "normal"
        },
    }
    co_route = []