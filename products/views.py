from django.http import HttpResponse, JsonResponse
from .models import Product, CustomUser, Category, Order, OrderItem, Address, Card
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomRegisterForm, LoginForm, AddressForm, CardForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
import hashlib
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# Create your views here.
def index(request):
    products = Product.objects.all()
    return render(request, '_main.html',
                  {'products': products})


def categories(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})

def register_view(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = CustomRegisterForm()
    return render(request, '_register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Invalid credentials')
    else:
        form = LoginForm()
    return render(request, '_login.html', {'form': form})

def logout_view(request):
    logout(request)  # This logs out the user
    return redirect('login')

@login_required
def cart_view(request):
    user = request.user
    cart_items = []
    for item in user.cart:
        product = Product.objects.get(id=item)  # Retrieve product using ID
        image_url = product.image_url
        cart_items.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'stock': product.stock,
            'image_url': image_url,
            'category': product.category_id.name if product.category_id else None
        })
    return render(request, 'cart.html', {'cart_items': cart_items})

@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    user = request.user
    if product_id not in user.cart:
        user.cart.append(product_id)  # Use list instead of set
        user.save()
    return HttpResponse(status=204)

@csrf_exempt
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        user = request.user
        if item_id in user.cart:
            user.cart.remove(item_id)  # Remove the item from the user's cart
            user.save()  # Save the updated user object
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Item not in cart'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def products_by_category(request):
    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()
    return render(request, 'products_by_category.html', {'products': products})

def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'search_results.html', {'products': products, 'query': query})

@login_required
def account_page(request):
    user = request.user
    addresses = user.addresses.all()
    cards = user.cards.all()
    orders = Order.objects.filter(user=user)
    return render(request, 'account.html', {
        'user': user,
        'addresses': addresses,
        'cards': cards,
        'orders': orders
    })

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('account')
    else:
        form = AddressForm()
    return render(request, 'add_address.html', {'form': form})

@login_required
def add_card(request):
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            return redirect('account')
    else:
        form = CardForm()
    return render(request, 'add_card.html', {'form': form})

@login_required
def checkout(request):
    if request.method == 'POST':
        address_id = request.POST.get('address')
        card_id = request.POST.get('card')
        cart_items = request.user.cart  # Use the user's cart directly

        if not cart_items:
            messages.error(request, "Your cart is empty.")
            return redirect('cart')

        total_price = 0
        for item_id in cart_items:
            product = Product.objects.get(id=item_id)
            total_price += product.price

        # Retrieve the selected address and card
        selected_address = get_object_or_404(Address, id=address_id, user=request.user)
        selected_card = get_object_or_404(Card, id=card_id, user=request.user)

        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            card_holder=selected_card.cardholder_name,  # Fixed attribute name
            card_last4=selected_card.card_number[-4:],
            address_street=selected_address.street,
            address_city=selected_address.city,
            address_state=selected_address.state,
            address_zip=selected_address.postal_code  # Fixed attribute name
        )

        for item_id in cart_items:
            product = Product.objects.get(id=item_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,  # Assuming quantity is 1 for simplicity
                price=product.price
            )
            # Decrease the stock of the product
            product.stock -= 1
            product.save()

        # Clear the cart
        request.user.cart = []
        request.user.save()

        messages.success(request, "Order created successfully!")
        return redirect('account')

    addresses = request.user.addresses.all()
    cards = request.user.cards.all()
    return render(request, 'checkout.html', {'addresses': addresses, 'cards': cards})

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect('account')

@login_required
def delete_card(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    card.delete()
    messages.success(request, "Card deleted successfully.")
    return redirect('account')

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {
        'order': order,
        'card_holder': order.card_holder,
        'card_last4': order.card_last4,
        'address_street': order.address_street,
        'address_city': order.address_city,
        'address_state': order.address_state,
        'address_zip': order.address_zip,
    })