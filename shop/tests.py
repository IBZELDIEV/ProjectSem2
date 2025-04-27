from django.test import TestCase
from shop.models import Category, Product

class CategoryProductModelTests(TestCase):
    # This method sets up the test data before each test method is run
    def setUp(self):
        # Create a Category object for the test
        self.category = Category.objects.create(name='Men')
        # Create a Product object that belongs to the 'Men' category
        self.product = Product.objects.create(
            category=self.category,
            name='Alien by Thierry Mugler',
            description='An iconic fragrance for men.',
            price=99.99,
            stock=20,
            available=True
        )

    # Test case to check if the category name is correctly set
    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Men')  
    # Test case to check the string representation method of the Category model
    def test_category_str_method(self):
        self.assertEqual(str(self.category), 'Men') 

    # Test case to check if the product is created with the correct attributes
    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Alien by Thierry Mugler') 
        self.assertEqual(self.product.description, 'An iconic fragrance for men.')  
        self.assertEqual(self.product.price, 99.99)  
        self.assertEqual(self.product.stock, 20)  
        self.assertEqual(self.product.category.name, 'Men')  

    # Test case to check the string representation method of the Product model
    def test_product_str_method(self):
        self.assertEqual(str(self.product), 'Alien by Thierry Mugler') 

    # Test case to check if the product price is greater than zero
    def test_product_price_positive(self):
        self.assertGreater(self.product.price, 0) 

    # Test case to check if the product stock is greater than zero
    def test_product_stock_positive(self):
        self.assertGreater(self.product.stock, 0)  

    # Test case to verify that the 'available' field is set to True by default for products
    def test_product_available_default_true(self):
        self.assertTrue(self.product.available) 

    # Test case to check the relationship between product and category
    def test_product_category_relation(self):
        self.assertEqual(self.product.category.name, 'Men')  

    # Test case to check if the product description contains the word 'fragrance'
    def test_product_description_content(self):
        self.assertIn('fragrance', self.product.description.lower())  
