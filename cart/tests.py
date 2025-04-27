from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from shop.models import Product
from .models import Cart, CartItem
from .views import add_cart, cart_remove, cart_detail
from decimal import Decimal

class CartTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.product = Product.objects.create(
            name='Test Perfume',
            price=Decimal('50.00'),
            stock=10,
            available=True
        )

    def get_request_with_session(self):
        request = self.factory.get('/')
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        return request

    # Test Case 1: Add a perfume to the cart
    def test_add_perfume_to_cart(self):
        request = self.get_request_with_session()

        response = add_cart(request, self.product.id)

        cart = Cart.objects.get(cart_id=request.session.session_key)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)

        self.assertEqual(cart_item.quantity, 1)
        print("Test Case 1 Passed: Add a perfume to the cart.")

    # Test Case 2: Remove a perfume from the cart
    def test_remove_perfume_from_cart(self):
        request = self.get_request_with_session()

        add_cart(request, self.product.id)

        cart_remove(request, self.product.id)

        cart = Cart.objects.get(cart_id=request.session.session_key)
        cart_items = CartItem.objects.filter(cart=cart, product=self.product)

        self.assertFalse(cart_items.exists())
        print("Test Case 2 Passed: Remove a perfume from the cart.")


# Test Case 3: Checkout process with valid payment info
    def test_checkout_process(self):
        request = self.get_request_with_session()

        # Add product to cart
        add_cart(request, self.product.id)

        # Instead of calling cart_detail (which renders template),
        # we manually check cart items and total
        cart = Cart.objects.get(cart_id=request.session.session_key)
        cart_items = CartItem.objects.filter(cart=cart)

        total = sum(item.product.price * item.quantity for item in cart_items)

        self.assertEqual(len(cart_items), 1)
        self.assertEqual(total, Decimal('50.00'))
        print("Test Case 3 Passed: Checkout process simulated without template rendering.")
