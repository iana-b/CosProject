from io import BytesIO

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from .models import Brand, Category, Product

TEST_STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}

SIGNUP_DATA = {
    'username': 'newbie',
    'email': 'newbie@example.com',
    'password1': 'zxcv!9876qwer',
    'password2': 'zxcv!9876qwer',
}


def png_upload():
    buffer = BytesIO()
    Image.new('RGB', (1, 1)).save(buffer, 'PNG')
    return SimpleUploadedFile('x.png', buffer.getvalue(), 'image/png')


@override_settings(STORAGES=TEST_STORAGES)
class CatalogTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.brand = Brand.objects.create(title='Brand')
        self.category = Category.objects.create(title='Category')
        self.alice = User.objects.create_user('alice', 'alice@example.com', 'pw12345678!')
        self.staff = User.objects.create_superuser('boss', 'boss@example.com', 'pw12345678!')

    def product(self, title='Product', status=Product.PUBLISHED, user=None):
        return Product.objects.create(
            title=title,
            brand=self.brand,
            category=self.category,
            picture='products/x.png',
            user=user or self.alice,
            status=status,
        )


class ProductModerationTests(CatalogTestCase):
    def add_product(self, title):
        return self.client.post('/product/new/', {
            'title': title,
            'brand': self.brand.pk,
            'category': self.category.pk,
            'picture': png_upload(),
        })

    def test_product_from_user_needs_moderation(self):
        self.client.force_login(self.alice)
        self.add_product('Крем')
        product = Product.objects.get(title='Крем')
        self.assertEqual(product.status, Product.DRAFT)
        self.assertEqual(product.user, self.alice)

    def test_product_from_staff_is_published(self):
        self.client.force_login(self.staff)
        self.add_product('Тоник')
        self.assertEqual(Product.objects.get(title='Тоник').status, Product.PUBLISHED)

    def test_anonymous_cannot_open_product_form(self):
        self.assertEqual(self.client.get('/product/new/').status_code, 302)

    def test_anonymous_cannot_post_review_or_purchase(self):
        product = self.product()
        self.assertEqual(self.client.post(f'/product/{product.pk}/review/').status_code, 302)
        self.assertEqual(self.client.post(f'/product/{product.pk}/purchase/').status_code, 302)

    def test_draft_is_hidden_from_catalog_and_search(self):
        draft = self.product(title='Черновик', status=Product.DRAFT)
        link = f'/product/{draft.pk}/'
        self.assertNotContains(self.client.get('/'), link)
        self.assertNotContains(self.client.get('/search/?q=Черновик'), link)

    def test_draft_is_visible_to_author_and_staff_only(self):
        draft = self.product(status=Product.DRAFT)
        self.assertEqual(self.client.get(f'/product/{draft.pk}/').status_code, 404)

        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(f'/product/{draft.pk}/').status_code, 200)

        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(f'/product/{draft.pk}/').status_code, 200)


class SignUpTests(CatalogTestCase):
    def test_filled_honeypot_is_rejected(self):
        self.client.post('/signup/', SIGNUP_DATA | {'website': 'http://spam'})
        self.assertFalse(User.objects.filter(username='newbie').exists())

    def test_signups_are_rate_limited_per_ip(self):
        for i in range(5):
            self.client.post('/signup/', SIGNUP_DATA | {
                'username': f'user{i}',
                'email': f'user{i}@example.com',
            })
        self.assertEqual(User.objects.filter(username__startswith='user').count(), 3)
