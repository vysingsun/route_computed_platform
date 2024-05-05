from django.urls import path
from . import views
from .api.views import RouteView, RouteViewTest, RequestRoute

# from .api.route import router

urlpatterns = [
    path('', views.CurrentView.index, name='index'),
    path('google_map', views.CurrentView.google_map, name='google_map'),
    path('open_street_map', views.CurrentView.open_street_map, name='open_street_map'),

    # path('api/',include(router.urls))
    # api
    path('api/v1/route', RouteView.as_view({'get': 'get_route_osrm_grab'}), name='get_route_osrm_grab'),
    path('api/v2/route', RouteView.as_view({'get': 'get_route_waze'}), name='get_route_waze'),
    # path('api/v2/route', RouteView.as_view({'get': 'get_route_waze'}), name='get_route_waze'),
    # path('api/route/:route/:rain', RouteView.as_view({'get': 'get_points'}), name='api_route'),
    path('api/set_traffic',RouteView.as_view({'post': 'set_traffic'})),
    # path('api/get_traffic',RouteView.as_view({'get': 'get_traffic'}))
    path('api/route/test/start=<str:lat>/end=<str:long>', RouteViewTest.as_view(), name='api_route_test'),
    # path('api/route/get_points', RequestRoute.as_view({'get': 'get_points'}))
]
