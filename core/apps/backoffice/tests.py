from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from core.apps.backoffice.models import Order, Category, Product

class OrderPrintViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user.user_permissions.add(
            Permission.objects.get(codename='can_print_order')
        )
        self.user.save()
        self.client.login(username='testuser', password='password')

        self.category = Category.objects.create(name="Test Cat")
        self.product = Product.objects.create(name="Test Prod", price=10, category=self.category)
        self.order = Order.objects.create(created_by=self.user, client_name="Client 1", total_amount=10)
        self.order.items.create(product=self.product, quantity=1, unit_price=10, subtotal=10)

    def test_print_order_view(self):
        url = reverse('backoffice:order_print', kwargs={'pk': self.order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')