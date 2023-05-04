from django.urls import include, path
from django.conf.urls import patterns
from rest_framework_bulk.routes import BulkRouter

from .views import SimpleViewSet


router = BulkRouter()
router.register('simple', SimpleViewSet, 'simple')

urlpatterns = patterns(
    '',

    path('api/', include(router.urls, namespace='api')),
)
