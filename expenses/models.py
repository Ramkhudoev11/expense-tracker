from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Категория")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    date = models.DateField(verbose_name="Дата")
    description = models.CharField(max_length=255, blank=True, verbose_name="Описание")

    def __str__(self):
        return f"{self.amount} руб. — {self.category}"

    class Meta:
        verbose_name = "Расход"
        verbose_name_plural = "Расходы"
        ordering = ['-date']


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    is_active = models.BooleanField(default=False, verbose_name="Активна")
    paddle_customer_id = models.CharField(max_length=255, blank=True, null=True)
    paddle_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} — {'Премиум' if self.is_active else 'Бесплатно'}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"