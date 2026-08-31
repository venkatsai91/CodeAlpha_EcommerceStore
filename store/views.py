from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from .models import Product, Order


def home(request):

    products = Product.objects.all()

    return render(
        request,
        'store/home.html',
        {'products': products}
    )


def product_detail(request, product_id):

    product = Product.objects.get(id=product_id)

    return render(
        request,
        'store/product_detail.html',
        {'product': product}
    )


def add_to_cart(request, product_id):

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session['cart'] = cart

    return redirect('cart')


def cart(request):

    cart_data = request.session.get('cart', {})

    products = []

    total = 0

    for product_id, quantity in cart_data.items():

        product = Product.objects.get(id=product_id)

        subtotal = product.price * quantity

        total += subtotal

        products.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(
        request,
        'store/cart.html',
        {
            'products': products,
            'total': total
        }
    )


def register(request):

    if request.method == 'POST':

        username = request.POST['username']

        email = request.POST['email']

        password = request.POST['password']

        if User.objects.filter(username=username).exists():

            return render(
                request,
                'store/register.html',
                {'error': 'Username already exists'}
            )

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('login')

    return render(
        request,
        'store/register.html'
    )


def login_view(request):

    if request.method == 'POST':

        username = request.POST['username']

        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('home')

        return render(
            request,
            'store/login.html',
            {
                'error':
                'Invalid username or password'
            }
        )

    return render(
        request,
        'store/login.html'
    )


def logout_view(request):

    logout(request)

    return redirect('home')


def checkout(request):

    if not request.user.is_authenticated:

        return redirect('login')

    cart_data = request.session.get('cart', {})

    if not cart_data:

        return redirect('cart')

    total = 0

    for product_id, quantity in cart_data.items():

        product = Product.objects.get(id=product_id)

        total += product.price * quantity

    Order.objects.create(
        user=request.user,
        total_amount=total
    )

    request.session['cart'] = {}

    return redirect('orders')


def orders(request):

    if not request.user.is_authenticated:

        return redirect('login')

    user_orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'store/orders.html',
        {'orders': user_orders}
    )