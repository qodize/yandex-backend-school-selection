from rest_framework import serializers
from delivery.models import Courier, Order


class CourierSerializer(serializers.ModelSerializer):
    courier_id = serializers.IntegerField()
    regions = serializers.ListField(child=serializers.IntegerField())
    working_hours = serializers.ListField(child=serializers.CharField(max_length=11))
    earnings = serializers.IntegerField(required=False)

    class Meta:
        model = Courier
        fields = ('courier_id', 'courier_type',
                  'regions', 'working_hours', 'earnings')

    def validate(self, attrs):
        unknown = set(self.initial_data) - set(self.fields)
        # if we are updating then courier_id must be read only
        if self.instance and self.initial_data.get('courier_id', False):
            unknown.add("courier_id")

        if unknown:
            raise serializers.ValidationError(
                {
                    "unknown_fields": list(unknown)
                }
            )
        try:
            if self.instance is None:
                Courier.objects.get(pk=self.initial_data['courier_id'])
                raise serializers.ValidationError(
                    f"courier_id must be unique: courier_id {self.initial_data['courier_id']}"
                )
        except Courier.DoesNotExist as e:
            pass

        return attrs

    def create(self, validated_data):
        return Courier.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.courier_type = validated_data.get('courier_type', instance.courier_type)
        instance.regions = validated_data.get('regions', instance.regions)
        instance.working_hours = validated_data.get('working_hours', instance.working_hours)
        instance.save()
        return instance


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('order_id', 'weight', 'region', 'delivery_hours')

    def validate(self, attrs):
        unknown = set(self.initial_data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError(
                {
                    "unknown_fields": list(unknown)
                }
            )
        try:
            if self.instance is None:
                Order.objects.get(pk=self.initial_data['order_id'])
                raise serializers.ValidationError(
                    f"order_id must be unique: order_id {self.initial_data['order_id']}"
                )
        except Order.DoesNotExist as e:
            pass

        return attrs

