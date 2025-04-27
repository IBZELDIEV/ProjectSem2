from django.core.mail import send_mail
from django.shortcuts import redirect, render, get_object_or_404
from shop.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
import stripe
from django.conf import settings
from django.urls import reverse
from order.models import Order, OrderItem
from stripe import StripeError
from vouchers.models import Voucher
from vouchers.forms import VoucherApplyForm
from decimal import Decimal

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
    
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
    
    return redirect('cart:cart_detail')

def cart_detail(request, total=0, counter=0, cart_items=None):
    discount = 0
    voucher = None
    new_total = 0

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)

        for cart_item in cart_items:
            product = cart_item.product
            price = product.sale_price if product.is_sale else product.price
            cart_item.sub_total = price * cart_item.quantity
            total += cart_item.sub_total
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        cart_items = []
        pass

    voucher_apply_form = VoucherApplyForm()

    try:
        voucher_id = request.session.get('voucher_id')
        voucher = Voucher.objects.get(id=voucher_id)
        if voucher:
            discount = (total * (voucher.discount / Decimal('100')))
            new_total = total - discount
        else:
            new_total = total
    except (Voucher.DoesNotExist, TypeError):
        voucher = None
        new_total = total

    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_total = int(new_total * 100)  # Stripe expects cents

    if request.method == 'POST':
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': 'Order from Perfect Perfume Store',
                        },
                        'unit_amount': stripe_total,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                billing_address_collection='required',
                payment_intent_data={'description': 'New order'},
                success_url=request.build_absolute_uri(reverse('cart:new_order')) + f"?session_id={{CHECKOUT_SESSION_ID}}&voucher_id={voucher.id if voucher else ''}&cart_total={total}",
                cancel_url=request.build_absolute_uri(reverse('cart:cart_detail')),
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return render(request, 'cart.html', {
                'cart_items': cart_items,
                'total': total,
                'counter': counter,
                'error': str(e),
            })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total,
        'counter': counter,
        'voucher_apply_form': voucher_apply_form,
        'voucher': voucher,
        'discount': discount,
        'new_total': new_total,
    })

def cart_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('cart:cart_detail')

def full_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart:cart_detail')

def empty_cart(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        cart_items.delete()
        cart.delete()
        return redirect('shop:all_products')
    except Cart.DoesNotExist:
        pass
    return redirect('cart:cart_detail')

def create_order(request):
    try:
        session_id = request.GET.get('session_id')
        cart_total = request.GET.get('cart_total')
        voucher_id = request.GET.get('voucher_id')
        if not session_id:
            raise ValueError("Session ID not found.")
        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except StripeError as e:
            return redirect("shop:all_products")
        
        customer_details = session.customer_details
        if not customer_details or not customer_details.address:
            raise ValueError("Missing information in the Stripe session.")
        
        billing_address = customer_details.address
        billing_name = customer_details.name
        shipping_address = customer_details.address
        shipping_name = customer_details.name

        order_details = Order.objects.create(
            token=session.id,
            total=session.amount_total / 100,
            emailAddress=customer_details.email,
            billingName=billing_name,
            billingAddress1=billing_address.line1,
            billingCity=billing_address.city,
            billingPostcode=billing_address.postal_code,
            billingCountry=billing_address.country,
            shippingName=shipping_name,
            shippingAddress1=shipping_address.line1,
            shippingCity=shipping_address.city,
            shippingPostcode=shipping_address.postal_code,
            shippingCountry=shipping_address.country,
        )
        order_details.save()

        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)

        if voucher_id:
            try:
                voucher = Voucher.objects.get(id=voucher_id)
                order_details.voucher = voucher
                cart_total = Decimal(cart_total)
                order_details.discount = cart_total * (voucher.discount / Decimal('100'))
                order_details.total = cart_total - order_details.discount
                order_details.save()
            except Voucher.DoesNotExist:
                pass

        for item in cart_items:
            oi = OrderItem.objects.create(
                product=item.product.name,
                quantity=item.quantity,
                price=item.product.price,
                order=order_details
            )
            oi.save()

            product = Product.objects.get(id=item.product.id)
            product.stock = max(0, int(product.stock - item.quantity))
            product.save()

        empty_cart(request)
        return redirect('order:thanks', order_details.id)

    except (ValueError, StripeError, Exception) as e:
        print(f"Error: {e}")
        return redirect("shop:all_products")

def send_email(request, order_id):
    try:
        send_mail(
            'Your order',
            'Thank you for your order!',
            'no-reply@onlineshop.com',
            ['p@c.ie'],
            fail_silently=False,
            html_message=f"<p>Dear {request.user.username},</p><p>Thank you for your order. Your order number is {order_id.id}</p>"
        )
    except Exception as e:
        print(f"Email failed: {e}")
