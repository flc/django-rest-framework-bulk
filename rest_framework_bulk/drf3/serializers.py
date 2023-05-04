import inspect

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ListSerializer

from django.utils.translation import ugettext_lazy as _


__all__ = [
    'BulkListSerializer',
    'BulkSerializerMixin',
]


class BulkSerializerMixin:
    def to_internal_value(self, data):
        ret = super().to_internal_value(data)

        id_attr = getattr(self.Meta, 'update_lookup_field', 'id')
        request_method = getattr(getattr(self.context.get('view'), 'request'), 'method', '')

        # add update_lookup_field field back to validated data
        # since super by default strips out read-only fields
        # hence id will no longer be present in validated_data
        if all((isinstance(self.root, BulkListSerializer),
                id_attr,
                request_method in ('PUT', 'PATCH'))):
            id_field = self.fields[id_attr]
            id_value = id_field.get_value(data)

            ret[id_attr] = id_value

        return ret


class BulkListSerializer(ListSerializer):
    update_lookup_field = 'id'

    def update(self, queryset, all_validated_data):
        id_attr = getattr(self.child.Meta, 'update_lookup_field', 'id')

        all_validated_data_by_id = {
            i.pop(id_attr): i
            for i in all_validated_data
        }

        if not all(bool(i) and not inspect.isclass(i)
                    for i in all_validated_data_by_id.keys()):
            raise ValidationError(
                _("The '%s' field is missing from the data.") % id_attr
                )

        # since this method is given a queryset which can have many
        # model instances, first find all objects to update
        # and only then update the models
        objects_to_update = queryset.filter(**{
            f'{id_attr}__in': all_validated_data_by_id.keys(),
        })

        if len(all_validated_data_by_id) != objects_to_update.count():
            raise ValidationError(_(
                "Could not find all objects to update. Make sure the values in "
                "the '%s' field refer to valid/existing objects.") % id_attr
                )

        self.validate_bulk_update(objects_to_update)

        updated_objects = []

        for obj in objects_to_update:
            obj_id = getattr(obj, id_attr)
            obj_validated_data = all_validated_data_by_id.get(obj_id)

            # use model serializer to actually update the model
            # in case that method is overwritten
            updated_objects.append(self.child.update(obj, obj_validated_data))

        return updated_objects

    def validate_bulk_update(self, objects):
        """
        Hook to ensure that the bulk update should be allowed.
        """
        pass
