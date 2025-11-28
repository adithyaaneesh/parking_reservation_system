from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ParkingLot, ParkingSlot, Reservation, Profile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ['id', 'username', 'email', 'is_staff']
        fields = ['id', 'username', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

class ParkingSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlot
        fields = ['id', 'lot', 'slot_number', 'status']

class ParkingLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = ['id', 'name', 'address', 'total_slots']


class ReservationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    slot = ParkingSlotSerializer(read_only=True)
    slot_id = serializers.PrimaryKeyRelatedField(source='slot', queryset=ParkingSlot.objects.all(), write_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'user', 'slot', 'slot_id', 'start_time', 'end_time', 'status', 'payment_status', 'qr_code'] 
        read_only_fields = ['status', 'payment_status', 'qr_code']




# def validate(self, data):
# start = data.get('start_time')
# end = data.get('end_time')
# if start >= end:
# raise serializers.ValidationError('end_time must be after start_time')
# return data


# def create(self, validated_data):
# user = self.context['request'].user
# slot = validated_data.pop('slot')
# # check overlap
# start = validated_data['start_time']
# end = validated_data['end_time']
# overlapping = Reservation.objects.filter(slot=slot, status='active').filter(
# start_time__lt=end, end_time__gt=start
# )
# if overlapping.exists():
# raise serializers.ValidationE