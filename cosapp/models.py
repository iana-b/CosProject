from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Brand(models.Model):
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField('название', max_length=50)
    brand = models.ForeignKey(Brand, verbose_name='бренд', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name='категория', on_delete=models.CASCADE)
    picture = models.ImageField('изображение', upload_to='products')

    def __str__(self):
        return self.title

    def get_average_rating(self):
        reviews = Review.objects.filter(product=self)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0

    def get_hearts_display(self):
        avg = self.get_average_rating()
        import math
        hearts_rating = math.ceil(avg)
        if hearts_rating == 1:
            return '💔'
        elif hearts_rating == 2:
            return '💛💛'
        elif hearts_rating == 3:
            return '🧡🧡🧡'
        elif hearts_rating == 4:
            return '🩷🩷🩷🩷'
        elif hearts_rating == 5:
            return '❤️❤️❤️❤️❤️'
        else:
            return ''


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField('стоимость', max_digits=6, decimal_places=2)
    date = models.DateField('дата', null=True)
    store = models.CharField('магазин', max_length=30)

    def __str__(self):
        return f'{self.user.username} - {self.product.title}'


RATING_CHOICES = [
    (1, '💔'),
    (2, '💛💛'),
    (3, '🧡🧡🧡'),
    (4, '🩷🩷🩷🩷'),
    (5, '❤️❤️❤️❤️❤️️'),
]


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField('рейтинг', choices=RATING_CHOICES)
    comment = models.TextField('комментарий')
    liked = models.BooleanField('понравилось ?', null=True)

    def __str__(self):
        return f'{self.user.username} - {self.product.title}'
