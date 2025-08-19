import stripe
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.conf import settings
from .models import Item, Order
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

def items_list(request):
    items = Item.objects.all()
    cart = request.session.get("cart", [])
    cart_count = len(cart)
    return render(request, "items_list.html", {"items": items, "cart_count": cart_count})

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, "item_detail.html", {"item": item, "stripe_public_key": settings.STRIPE_PUBLIC_KEY})

def cart_detail(request):
    cart = request.session.get('cart', [])
    items = Item.objects.filter(id__in=cart)
    total = sum(item.price for item in items)
    cart_currency = items.first().currency if items.exists() else 'rub'
    return render(request, 'cart.html', {
        'items': items,
        'total': total,
        'cart_currency': cart_currency
    })

def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    order_id = request.session.get("order_id")

    if order_id:
        order = get_object_or_404(Order, id=order_id)
        if order.items.exists() and order.items.first().currency != item.currency:
            messages.error(request, "Все товары в корзине должны быть одной валюты")
            return redirect("items-list") 
    else:
        order = Order.objects.create(currency=item.currency)
        request.session["order_id"] = order.id

    order.items.add(item)
    order.calculate_total()

    cart = request.session.get("cart", [])
    cart.append(item.id)
    request.session["cart"] = cart

    messages.success(request, f"Товар {item.name} добавлен в корзину")
    return redirect("cart-detail")

def remove_from_cart(request, item_id):
    cart = request.session.get("cart", [])
    if item_id in cart:
        cart.remove(item_id)
        request.session["cart"] = cart

    order_id = request.session.get("order_id")
    if order_id:
        order = get_object_or_404(Order, id=order_id)
        order.items.remove(item_id)
        order.calculate_total()

    return redirect("cart-detail")

def buy_cart(request):
    order_id = request.session.get("order_id")
    if not order_id:
        return JsonResponse({"error": "Корзина пуста"})

    order = get_object_or_404(Order, id=order_id)
    order.calculate_total()

    if order.total_amount < 1: 
        return JsonResponse({"error": "Сумма заказа слишком мала для оплаты Stripe"})

    keys = settings.STRIPE_KEYS[order.items.first().currency]
    stripe.api_key = keys["secret"]

    line_items = []
    for item in order.items.all():
        line_items.append({
            "price_data": {
                "currency": item.currency,
                "product_data": {"name": item.name, "description": item.description},
                "unit_amount": item.price * 100, 
            },
            "quantity": 1,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=request.build_absolute_uri("/success/"),
        cancel_url=request.build_absolute_uri("/cancel/"),
    )

    return JsonResponse({"id": session.id, "public_key": keys["public"]})



@csrf_exempt
def buy_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    order = Order.objects.create(currency=item.currency)
    order.items.add(item)
    order.calculate_total()

    keys = settings.STRIPE_KEYS[item.currency]
    stripe.api_key = keys["secret"]

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": item.currency,
                "product_data": {"name": item.name, "description": item.description},
                "unit_amount": item.price * 100,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=request.build_absolute_uri("/success/"),
        cancel_url=request.build_absolute_uri("/cancel/"),
        metadata={"order_id": str(order.id)},
    )

    return JsonResponse({"id": session.id, "public_key": keys["public"]})

def success(request):
    return render(request, "success.html")


def cancel(request):
    return render(request, "cancel.html")
