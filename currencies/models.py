from django.db import models

class Currency(models.Model):
    """
    Represents a currency and its exchange rate against EUR.
    """

    def __str__(self):
        return "{0.name}: {0.rate}".format(self)

    class Meta:
        verbose_name_plural = 'currencies'

    name = models.CharField(max_length=3)
    rate = models.FloatField()

class Sum(models.Model):
    """
    Represents a sum with an amount and a currency.
    """
    def __str__(self):
        return "{} {}".format(self.amount, self.currency.name)

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='sums')
