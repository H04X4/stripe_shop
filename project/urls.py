from django.contrib import admin
from django.urls import path
from shop import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove-from-cart'),
    path("", views.items_list, name="items-list"),
    path("item/<int:item_id>/", views.item_detail, name="item-detail"),
    path("buy/<int:item_id>/", views.buy_item, name="buy-item"),
    path("success/", views.success, name="success"),
    path("cancel/", views.cancel, name="cancel"),
    path("cart/", views.cart_detail, name="cart-detail"),
    path("cart/add/<int:item_id>/", views.add_to_cart, name="add-to-cart"),
    path("cart/buy/", views.buy_cart, name="buy-cart"),
]