from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, CartItem, Favorite, Order, OrderItem
from .forms import CustomUserCreationForm, OrderForm
from reportlab.pdfgen import canvas
from django.template.loader import render_to_string



def product_list(request):
    products = Product.objects.all()
    return render(request, 'core/product.html', {'products': products})

def home(request):
    return render(request, 'core/home.html')

def favorites(request):
    if request.user.is_authenticated:
        favorite_items = Favorite.objects.filter(user=request.user)
        favorite_products = [favorite.products.all() for favorite in favorite_items]
        context = {'favorite_products': favorite_products}
        return render(request, 'core/favorites.html', context)
    else:
        return redirect("login")

def login_user_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect('product')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return render(request, 'core/home.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    category_name = request.GET.get('category')
    if category_name:
        products = products.filter(category__name=category_name)

    return render(request, 'core/product.html', {'products': products, 'categories': categories})

def save_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        user = request.user
        if user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.success(request, f'{product.title} додано до корзини.')
        else:
            messages.error(request, 'Користувач не аутентифікований.')
            return redirect('login')
    else:
        messages.error(request, 'Метод не підтримується.')
    return redirect('product')
    

def cart(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        context = {'cart_items': cart_items, 'total_price': total_price}
        return render(request, 'core/cart.html', context)
    else:
        messages.error(request, 'Будь ласка, увійдіть, щоб переглянути свою корзину.')
        return redirect('login')
    
def delete_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id)
    if cart_item.user == request.user:
        cart_item.delete()
        messages.success(request, 'Товар успішно видалено з корзини.')
    else:
        messages.error(request, 'Ви не маєте дозволу видаляти цей товар з корзини.')
    return redirect('cart')

def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            cart_items = CartItem.objects.filter(user=request.user)
            for cart_item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity
                )
            cart_items.delete()
            
            return render(request, 'core/order_confirmation.html', {'order': order.id})
    else:
        form = OrderForm()
    return render(request, 'core/order.html', {'form': form})



def order_confirmation(request, order_id):
    return render(request, 'core/order_confirmation.html', {'order': order_id})


def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.user.is_authenticated:
        favorites, created = Favorite.objects.get_or_create(user=request.user)
        favorites.products.add(product)
    return redirect('product')

def remove_from_favorites(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.user.is_authenticated:
        favorites = Favorite.objects.get(user=request.user)
        favorites.products.remove(product)
    return redirect('favorites')


def create_ticket_pay(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    purchased_products = order.purchased_products_list()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'
    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Order #{order.id}")
    p.drawString(100, 780, "Purchased Products:")
    y = 760
    for index, product_info in enumerate(purchased_products, start=1):
        product_str = f"{index}. {product_info['title']}: {product_info['price']} грн x {product_info['quantity']} = {product_info['total_price']} грн"
        p.drawString(100, y, product_str)
        y -= 20
    p.showPage()
    p.save()
    return response


def add_to_cart_from_favorites(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.user.is_authenticated:
        user = request.user
        cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.success(request, f'{product.title} added to cart.')
    else:
        messages.error(request, 'User is not authenticated.')
        return redirect('login')
    return redirect('favorites')
