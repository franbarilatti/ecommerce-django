from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
        
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []

    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(product=product, cart=cart)

    # En lugar de usar conjuntos de objetos, usa listas ordenadas de valores
    ex_var_list = []
    id = []

    for item in cart_items:
        existing_variations = list(item.variations.all().values_list('id', flat=True))  # Obtén solo los IDs
        existing_variations.sort()  # Ordena para asegurar la comparación correcta
        ex_var_list.append(existing_variations)
        id.append(item.id)

    # Convierte las variaciones seleccionadas en una lista ordenada
    product_variation_ids = [var.id for var in product_variation]
    product_variation_ids.sort()

    # Ahora compara listas ordenadas en lugar de conjuntos de objetos
    if product_variation_ids in ex_var_list:
        index = ex_var_list.index(product_variation_ids)
        item_id = id[index]
        item = CartItem.objects.get(id=item_id)
        item.quantity += 1
        item.save()
    else:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1
        )
        if product_variation:
            cart_item.variations.add(*product_variation)
        
        if product_variation:
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect('cart')
        

def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    
    try:
        cart_item = CartItem.objects.filter(product=product, cart=cart, id=cart_item_id).first()
        
        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
    except:
        pass
    
    return redirect('cart')
    

def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    
    return redirect('cart')



def cart(request, total=0, quantity=0, cart_item=None):
    tax = 0
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = total + tax
    
    except ObjectDoesNotExist:
        pass     
    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        }
    
        
    return render(request, 'store/cart.html', context)