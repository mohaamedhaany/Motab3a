from django.db import models
from django.utils import timezone

# جدول الفلوس المقدم (العهدة)
class AdvancePayment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ المقدم")
    date_received = models.DateField(default=timezone.now, verbose_name="تاريخ الاستلام")
    note = models.CharField(max_length=255, blank=True, null=True, verbose_name="ملاحظات")
    
    # السطر الجديد اللي ضفناه عشان التصفير
    is_settled = models.BooleanField(default=False, verbose_name="تم تصفير الحساب؟")

    def __str__(self):
        return f"مقدم: {self.amount} - يوم {self.date_received}"

# جدول الطلبات اللي بيطلبها المدير
class Order(models.Model):
    item_name = models.CharField(max_length=200, verbose_name="الصنف / الطلب")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر")
    date_requested = models.DateField(default=timezone.now, verbose_name="تاريخ الطلب")
    
    is_settled = models.BooleanField(default=False, verbose_name="تم الحساب؟")

    def __str__(self):
        return f"{self.item_name} - {self.price} جنيه"