from django.urls import path

from . import views

urlpatterns = [
    path("orders/", views.orders, name="orders"),
    path("orders/<int:order_id>/", views.order_detail, name="order-detail"),
    path(
        "orders/<int:order_id>/recommendation/",
        views.order_recommendation,
        name="order-recommendation",
    ),
]