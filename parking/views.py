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
import razorpay
from django.conf import settings
import qrcode
import io
from django.http import HttpResponse

User = get_user_model()

class ProfileCreateView(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


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


def is_admin(user):
    return user.is_staff or user.is_superuser


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_parkingLot(request):
    if not is_admin(request.user):
        return Response({"error": "Not authorized"}, status=403)

    is_many = isinstance(request.data, list)
    serializer = ParkingLotSerializer(data=request.data, many=is_many)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_parkinglot(request, id):
    if not is_admin(request.user):
        return Response({"error": "Not authorized"}, status=403)

    parkinglot = get_object_or_404(ParkingLot, id=id)
    partial_update = request.method == 'PATCH'
    serializer = ParkingLotSerializer(instance=parkinglot, data=request.data, partial=partial_update)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_parkinglot(request, id):
    if not is_admin(request.user):
        return Response({"error": "Not authorized"}, status=403)

    parkinglot = get_object_or_404(ParkingLot, id=id)
    parkinglot.delete()
    return Response({"message": "ParkingLot deleted successfully!!!"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_parkingSlot(request):
    if not is_admin(request.user):
        return Response({"error": "Not authorized"}, status=403)

    is_many = isinstance(request.data, list)
    serializer = ParkingSlotSerializer(data=request.data, many=is_many)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_parking_slot(request, id):
    if not is_admin(request.user):
        return Response({"error": "Not authorized"}, status=403)

    parkingslot = get_object_or_404(ParkingSlot, id=id)
    partial_update = request.method == 'PATCH'
    serializer = ParkingSlotSerializer(instance=parkingslot, data=request.data, partial=partial_update)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_users(request):
    if not is_admin(request.user):
        return Response({"error": "Not authorized"}, status=403)

    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_reservations(request):
    if not is_admin(request.user):
        return Response({"error": "Not authorized"}, status=403)

    reservations = Reservation.objects.all()
    serializer = ReservationSerializer(reservations, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_parkinglot(request):
    parkinglot = ParkingLot.objects.all()
    serializer = ParkingLotSerializer(parkinglot, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_parkingSlot(request):
    parkingslot = ParkingSlot.objects.all()
    serializer = ParkingSlotSerializer(parkingslot, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_parkingSlot(request):
    available_parkingslot = ParkingSlot.objects.filter(status='open')
    serializer = ParkingSlotSerializer(available_parkingslot, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reserve_parkingslot(request):
    user = request.user

    data = request.data.copy()
    data.pop("id", None)

    slot_id = data.get("slot_id")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    amount = data.get("amount", 100)

    if not slot_id or not start_time or not end_time:
        return Response({"error": "slot_id, start_time and end_time are required."})

    try:
        slot = ParkingSlot.objects.get(id=slot_id)
    except ParkingSlot.DoesNotExist:
        return Response({"error": "Parking slot not found."})

    if slot.status != "open":
        return Response({"error": "This slot is not available."})

    overlapping = Reservation.objects.filter(
        slot=slot,
        start_time__lt=end_time,
        end_time__gt=start_time,
        status="active"
    ).exists()

    if overlapping:
        return Response({"error": "Slot already reserved for this time range."})

    data["slot_id"] = slot_id

    serializer = ReservationSerializer(data=data)
    if serializer.is_valid():
        reservation = serializer.save(user=user, amount=amount)

        slot.status = "held"
        slot.save()

        return Response(ReservationSerializer(reservation).data)

    return Response(serializer.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_reservations(request):
    user = request.user
    reservations = Reservation.objects.filter(user=user).order_by('-id')
    serializer = ReservationSerializer(reservations, many=True)
    return Response(serializer.data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_reservation(request):
    user = request.user
    reservation_id = request.data.get("reservation_id")

    if not reservation_id:
        return Response({"error": "reservation_id is required."})

    try:
        reservation = Reservation.objects.get(id=reservation_id, user=user)
    except Reservation.DoesNotExist:
        return Response({"error": "Reservation not found."})

    if reservation.status != "active":
        return Response({"error": "Only active reservations can be cancelled."})

    reservation.status = "cancelled"
    reservation.save()

    slot = reservation.slot
    slot.status = 'open'
    slot.save()

    return Response({"success": f"Reservation {reservation_id} cancelled successfully."})


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pay_for_reservation(request):
    reservation_id = request.data.get('reservation_id')

    if not reservation_id:
        return Response({"error": "reservation_id is required."}, status=400)

    try:
        reservation = Reservation.objects.get(id=reservation_id, user=request.user)
    except Reservation.DoesNotExist:
        return Response({"error": "Reservation not found."}, status=404)

    if reservation.payment_status == 'paid':
        return Response({"message": "Reservation already paid."})

    amount_in_paise = int(reservation.amount * 100)

    payment_link = razorpay_client.payment_link.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "description": f"Payment for Reservation {reservation.id}",
        "customer": {
            "name": reservation.user.username,
            "email": reservation.user.email
        },
        "notify": {
            "sms": True,
            "email": True
        },
        "callback_url": "http://127.0.0.1:8000/api/verify-payment"
    })

    reservation.razorpay_order_id = payment_link["id"]
    reservation.save()

    return Response({
        "reservation_id": reservation.id,
        "payment_link_id": payment_link["id"],
        "payment_url": payment_link["short_url"],
        "amount": reservation.amount
    })



@api_view(['POST'])
@permission_classes([AllowAny])
def verify_payment(request):
    razorpay_order_id = request.data.get("razorpay_order_id")
    razorpay_payment_id = request.data.get("razorpay_payment_id")
    razorpay_signature = request.data.get("razorpay_signature")

    if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
        return Response({"error": "Missing payment details"}, status=400)

    try:
        reservation = Reservation.objects.get(razorpay_order_id=razorpay_order_id)
    except Reservation.DoesNotExist:
        return Response({"error": "Reservation not found"}, status=404)

    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })
    except:
        reservation.payment_status = "failed"
        reservation.save()
        return Response({"error": "Payment verification failed"}, status=400)

    reservation.payment_status = "paid"
    reservation.status = "active"
    reservation.razorpay_payment_id = razorpay_payment_id
    reservation.razorpay_signature = razorpay_signature
    reservation.save()

    return Response({"success": "Payment verified successfully!"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reservation_qr_code(request, reservation_id):
    try:
        reservation = Reservation.objects.get(id=reservation_id, user=request.user)
    except Reservation.DoesNotExist:
        return Response({"error": "Reservation not found."}, status=404)

    # If no payment link created earlier → create it
    if not reservation.razorpay_order_id:
        amount_in_paise = int(reservation.amount * 100)

        payment_link = razorpay_client.payment_link.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "description": f"Payment for Reservation {reservation.id}",
            "customer": {
                "name": reservation.user.username,
                "email": reservation.user.email,
            },
            "notify": {
                "sms": True,
                "email": True
            },
            "callback_url": "http://127.0.0.1:8000/api/verify-payment"
        })


        reservation.razorpay_order_id = payment_link["id"]
        reservation.save()

        payment_url = payment_link["short_url"]

    else:
        payment_link = razorpay_client.payment_link.fetch(reservation.razorpay_order_id)
        payment_url = payment_link["short_url"]

    # Generate proper payment QR
    qr = qrcode.make(payment_url)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_all_reservations(request):
    if not is_admin(request.user):
        return Response({"error": "Not authorized"}, status=403)

    active_reservations = Reservation.objects.filter(status="active")

    if not active_reservations.exists():
        return Response({"message": "No active reservations found."})

    for reservation in active_reservations:
        reservation.status = "cancelled"
        reservation.save()

        slot = reservation.slot
        slot.status = "open"
        slot.save()

    return Response({"success": f"Cancelled {active_reservations.count()} active reservations."})
