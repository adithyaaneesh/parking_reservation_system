from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from .serializers import ParkingLotSerializer, ParkingSlotSerializer, ReservationSerializer, UserSerializer
from .models import ParkingSlot, ParkingLot, Reservation
from rest_framework.response import Response
from django.contrib.auth import get_user_model


# Create your views here.

User = get_user_model()

# admin add parkinglot 
@api_view(['POST'])
def add_parkingLot(request):
    is_many = isinstance(request.data,list)
    serializer = ParkingLotSerializer(data = request.data, many = is_many)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

# admin update parkinglot
@api_view(['PUT', 'PATCH'])
def update_parkinglot(request,id):
    parkinglot = get_object_or_404(ParkingLot,id=id)

    partial_update = True if request.method  == 'PATCH' else False

    serializer = ParkingLotSerializer(instance = parkinglot,data = request.data,partial = partial_update )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

# admin delete parkinglot
@api_view(['DELETE'])
def delete_parkinglot(request, id):
    Parkinglot = get_object_or_404(ParkingLot,id=id)
    Parkinglot.delete()
    return Response({"message":"ParkingLot deleted successfully!!!"})


#admin add parkingSlot
@api_view(['POST'])
def add_parkingSlot(request):
    is_many = isinstance(request.data, list)
    serializer = ParkingSlotSerializer(data = request.data, many = is_many)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

# admin update parkingSlot
@api_view(['PUT' , 'PATCH'])
def update_parking_slot(request, id):
    parkingslot = get_object_or_404(ParkingSlot, id=id)
    partial_update = True if request.method == 'PATCH' else False
    
    serializer = ParkingSlotSerializer(instance=parkingslot, data=request.data, partial=partial_update)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

# admin view all users
@api_view(['GET'])
def view_all_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

# admin view all reservations
@api_view(['GET'])
def view_all_reservations(request):
    reservations = Reservation.objects.all()
    serializer = ReservationSerializer(reservations, many =True)
    return Response(serializer.data)


# view all parkingLot 
@api_view(['GET'])
def all_parkinglot(request):
    parkinglot = ParkingLot.objects.all()
    serializer = ParkingLotSerializer(parkinglot, many =True)
    return Response(serializer.data)

# view all real_time parkingSlot
@api_view(['GET'])
def all_parkingSlot(request):
    parkingslot = ParkingSlot.objects.all()
    serializer = ParkingSlotSerializer(parkingslot, many=True)
    return Response(serializer.data)

# view all real time parking slot availability
# reserve a parkingslot for a specific time range
# cancel reservation
# pay for reservation
# get a QR code ticket