from rest_framework import serializers
from ..models import RouteTest

class RouteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RouteTest
        fields = ('id','start', 'end')
