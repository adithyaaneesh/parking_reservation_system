from django.urls import path
from . import views

urlpatterns = [
    # admin urls
    path("api/parkinglot/add/", views.add_parkingLot, name='add_parkinglot'),
    path("api/parkinglot/update/<int:id>/", views.update_parkinglot, name='update_parkinglot'),
    path("api/parkinglot/delete/<int:id>", views.delete_parkinglot, name='delete_parkinglot'),

    path("api/parkingslot/add/", views.add_parkingSlot, name='add_parkingslot'),
    path("api/parkingslot/update/<int:id>/", views.update_parking_slot, name='update_parkingslot'),

    path("api/all_reservation/", views.view_all_reservations, name='all_reservation'),
    path("api/all_users/", views.view_all_users, name='all_users'),

    # user urls
    path("api/all_parkinglot/", views.all_parkinglot, name='all_parkinglot'),
    path("api/all_parkingslot/", views.all_parkingSlot, name='all_parkingslot'),
    

]
