from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer):
    result = serializers.BooleanField()
    code = serializers.IntegerField()
    message = serializers.CharField()
    data = serializers.JSONField()


class SerializerBuilder:
    serializer = None

    def __init__(self, *, resource_class=None, data_serializer=None, name=None, **kwargs):
        self.serializer = self.build_serializer(
            resource_class=resource_class, data_serializer=data_serializer, name=name, **kwargs
        )

    def build_serializer(self, *, resource_class=None, data_serializer=None, name=None, **kwargs):
        raise NotImplementedError


class ResponseBuilder(SerializerBuilder):
    def build_serializer(self, *, resource_class=None, data_serializer=None, name=None, **kwargs):
        raise NotImplementedError


class PaginatorResponseBuilder(ResponseBuilder):
    def build_serializer(self, *, resource_class=None, data_serializer=None, name=None, **kwargs):
        class PaginatorSerializer(serializers.Serializer):
            page = serializers.IntegerField()
            num_pages = serializers.IntegerField()
            total = serializers.IntegerField()
            results = data_serializer

            class Meta:
                ref_name = "[{}]".format(name or resource_class.__name__)

        return PaginatorSerializer()


class StandardResponseBuilder(ResponseBuilder):
    def build_serializer(self, *, resource_class=None, data_serializer=None, name=None, **kwargs):
        class ResponseSerializer(serializers.Serializer):
            result = serializers.BooleanField()
            code = serializers.IntegerField()
            message = serializers.CharField()
            request_id = serializers.CharField()
            data = data_serializer

            class Meta:
                ref_name = name or "{}.{}".format(resource_class.__module__, resource_class.__name__)

        return ResponseSerializer()
