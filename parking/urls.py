from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [

    path("api/register", views.user_register, name='register'),
    path("api/login", views.user_login, name='login'),


    # admin urls
    path("api/parkinglot/add", views.add_parkingLot, name='add_parkinglot'),
    path("api/parkinglot/update/<int:id>", views.update_parkinglot, name='update_parkinglot'),
    path("api/parkinglot/delete/<int:id>", views.delete_parkinglot, name='delete_parkinglot'),

    path("api/parkingslot/add", views.add_parkingSlot, name='add_parkingslot'),
    path("api/parkingslot/update/<int:id>", views.update_parking_slot, name='update_parkingslot'),

    path("api/all_reservation", views.view_all_reservations, name='all_reservation'),
    path("api/all_users", views.view_all_users, name='all_users'),

    # user urls
    path("api/all_parkinglot", views.all_parkinglot, name='all_parkinglot'),
    path("api/all_parkingslot", views.all_parkingSlot, name='all_parkingslot'),
    path("api/available_parkingslot", views.available_parkingSlot, name='available_parkingslot'),
    path("api/reserve_parkingslot", views.reserve_parkingslot, name='reserve_parkingslot'),
    path("api/cancel_reservation", views.cancel_reservation, name='cancel_reservation'),
    path("api/reservation/<int:reservation_id>/qr/", views.reservation_qr_code, name="reservation_qr"),
    path('api/pay_reservation', views.pay_for_reservation, name='pay_for_reservation'),
    path("api/verify-payment", views.verify_payment, name='verify_payment'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)