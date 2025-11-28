from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .serializers import (ParkingLotSerializer, ParkingSlotSerializer, ReservationSerializer, UserSerializer, ProfileSerializer)
from .models import ParkingSlot, ParkingLot, Reservation, Profile




# Create your views here.

class ProfileCreateView(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def user_register(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")

    if not username or not password:
        return Response({"error": "Username and password required"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)

    user = User.objects.create_user(username=username, password=password, email=email)
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "message": "User registered successfully",
        "token": token.key,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password required"}, status=400)

    user = authenticate(username=username, password=password)

    if not user:
        return Response({"error": "Invalid credentials"}, status=400)

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "message": "Login successful",
        "token": token.key,
        "user": {
            "id": user.id,
            "username": user.username,
        }
    })


# admin add parkinglot 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_parkingLot(request):
    is_many = isinstance(request.data,list)
    serializer = ParkingLotSerializer(data = request.data, many = is_many)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

# admin update parkinglot
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def delete_parkinglot(request, id):
    Parkinglot = get_object_or_404(ParkingLot,id=id)
    Parkinglot.delete()
    return Response({"message":"ParkingLot deleted successfully!!!"})


#admin add parkingSlot
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_parkingSlot(request):
    is_many = isinstance(request.data, list)
    serializer = ParkingSlotSerializer(data = request.data, many = is_many)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

# admin update parkingSlot
@api_view(['PUT' , 'PATCH'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def view_all_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

# admin view all reservations
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_reservations(request):
    reservations = Reservation.objects.all()
    serializer = ReservationSerializer(reservations, many =True)
    return Response(serializer.data)


# view all parkingLot 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_parkinglot(request):
    parkinglot = ParkingLot.objects.all()
    serializer = ParkingLotSerializer(parkinglot, many =True)
    return Response(serializer.data)

# view all  parkingSlot
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_parkingSlot(request):
    parkingslot = ParkingSlot.objects.all()
    serializer = ParkingSlotSerializer(parkingslot, many=True)
    return Response(serializer.data)

# view all available parking slot 

# reserve a parkingslot for a specific time range
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reserve_parkingslot(request):
    user = request.user
    slot_id = request.data.get("slot_id")
    start_time = request.data.get("start_time")
    end_time = request.data.get("end_time")
    if not slot_id or not start_time or not end_time:
        return Response({"error":"slot_id, start_time and end_time are required."})
    
    try:
        slot=ParkingSlot.objects.get(id=slot_id)
    except ParkingSlot.DoesNotExist:
        return Response({"error": "Parking slot not found."})
    
    if slot.status != "available":
        return Response({"error":"This slot is not available."})
    overlapping = Reservation.objects.filter(
        slot=slot,
        start_time__lt = end_time,
        end_time__gt = start_time,
        status = "active"
    ).exists()
    if overlapping:
        return Response({"error": "Slot already reserved for this time range."})
    serializer = ReservationSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save(user=user, slot=slot)
        return Response(serializer.data)
    return Response(serializer.errors)

    


# cancel reservation
# pay for reservation
# get a QR code ticket