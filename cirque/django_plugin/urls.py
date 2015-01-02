# from django.conf.urls import include, url
# from django.contrib import admin
#
# urlpatterns = [
#     url(r'^$', 'cirque.django_plugin.views.main', name='main'),
#     url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
#
#     # url(r'^admin/', include(admin.site.urls)),
# ]


from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from django_plugin.models import CJDNSRoute


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CJDNSRouteSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = CJDNSRoute


class CJDNSRouterSet(viewsets.ModelViewSet):
    queryset = CJDNSRoute.objects.all()
    serializer_class = CJDNSRouteSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'cjdnsroutes', CJDNSRouterSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    url(r'^$', 'cirque.django_plugin.views.main', name='main'),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
