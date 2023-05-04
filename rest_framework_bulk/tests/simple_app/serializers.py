from rest_framework.serializers import ModelSerializer
from rest_framework_bulk.serializers import BulkListSerializer, BulkSerializerMixin

from .models import SimpleModel


class SimpleSerializer(BulkSerializerMixin,  # only required in DRF3
                       ModelSerializer):
    class Meta:
        model = SimpleModel
        # only required in DRF3
        list_serializer_class = BulkListSerializer
