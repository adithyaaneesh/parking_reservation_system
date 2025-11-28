from django.conf import settings
from django.db import models
from PIL import Image
import qrcode
import io
from django.core.files.base import ContentFile

User = settings.AUTH_USER_MODEL

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="profile_images/")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photo:
            img = Image.open(self.photo.path)
            if img.height > 800 or img.width > 800:
                img.thumbnail((800, 800))
                img.save(self.photo.path)


class ParkingLot(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    total_slots = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class ParkingSlot(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('inactive', 'Inactive'),
    ]

    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name='slots')
    slot_number = models.PositiveIntegerField()
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='available')

    class Meta:
        unique_together = ['lot', 'slot_number']

    def __str__(self):
        return f"{self.lot.name} - {self.slot_number}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name='reservations')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    qr_code = models.ImageField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Razorpay Required Fields (Added Correctly)
    razorpay_order_id = models.CharField(max_length=200, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=200, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=200, null=True, blank=True)

    def save(self, *args, **kwargs):
        # First save to create ID
        if not self.id:
            super().save(*args, **kwargs)

        # --- Generate QR Code ---
        qr_data = (
            f"Reservation ID: {self.id}\n"
            f"User: {self.user.username}\n"
            f"Slot: {self.slot.slot_number}\n"
            f"Start: {self.start_time}\n"
            f"End: {self.end_time}\n"
            f"Status: {self.status}"
        )

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, "PNG")

        self.qr_code.save(
            f"reservation_{self.id}.png",
            ContentFile(buffer.getvalue()),
            save=False
        )

        # Second save, only updating QR code
        super().save(update_fields=["qr_code"])


class Payment(models.Model):
    PROVIDERS = [
        ('razorpay', 'Razorpay'),
    ]

    reservation = models.ForeignKey(Reservation, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.CharField(max_length=50, choices=PROVIDERS)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} {self.status}"
