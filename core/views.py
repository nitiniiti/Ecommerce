from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, OrderItem, Order
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.contrib import messages

# Create your views here.


# def products(request):
#     context = {
#         "items": Item.objects.all()
#     }
#     return render(request, "products.html", context)


def checkout(request):

    return render(request, "checkout.html")


# def home(request):

#     context = {
#         "items": Item.objects.all()
#     }
#     return render(request, "home.html", context)

class HomeView(ListView):
    model = Item
    template_name = "home.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated")
            return redirect("core:product", slug=slug)
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart")
            return redirect("core:product", slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")
        return redirect("core:product", slug=slug)


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)

    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart")
        else:
            # Add a message saying the order doesn't contain this order item
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        # Add a message saying the user doesn't have an order
        messages.info(request, "You don't have an active order")
        return redirect("core:product", slug=slug)
    return redirect("core:product", slug=slug)
