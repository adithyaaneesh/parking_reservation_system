from django.conf import settings
from django.db import models
from PIL import Image


class Profile(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="profile_images/")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.photo.path)

        if img.height > 800 or img.width > 800:
            img.thumbnail((800, 800))
            img.save(self.photo.path)

# Create your models here.

User = settings.AUTH_USER_MODEL

class ParkingLot(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    total_slots = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
class ParkingSlot(models.Model):
    STATUS_CHOICES =[
        ('available','Available'),
        ('reserved','Reserved'),
        ('inactive','Inactive'),
    ]
    
    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name='slots')
    slot_number = models.PositiveIntegerField()
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='available')

    class Meta:
        unique_together = ['lot', 'slot_number']

    def __str__(self):
        return f"{self.lot.name} - {self.slot_number}"
    
class Reservation(models.Model):
    STATUS = [
        ('active','Active'),
        ('completed','Completed'),
        ('cancelled','Cancelled'),
    ]
    PAYMENT = [
        ('pending','Pending'),
        ('paid','Paid'),
        ('failed','Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name='reservations')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS, default='active')
    payment_status = models.CharField(max_length=20, choices=PAYMENT, default='pending')
    qr_code = models.ImageField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation {self.id} by {self.user}"


# class Payment(models.Model):
#     PROVIDERS = [
#         ('razorpay', 'Razorpay'),
#     ]
#     reservation = models.ForeignKey(Reservation, related_name='payments', on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     provider = models.CharField(max_length=50, choices=PROVIDERS)
#     transaction_id = models.CharField(max_length=255, blank=True, null=True)
#     status = models.CharField(max_length=50, default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)
# def __str__(self):
#     return f"Payment {self.id} {self.status}"

