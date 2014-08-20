from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^$', 'cirque.django.views.main', name='main'),

    # url(r'^admin/', include(admin.site.urls)),
]
