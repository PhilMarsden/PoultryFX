from django.db import models
from django.contrib.auth.models import User


class IGPL(models.Model):
    closing_ref = models.CharField(max_length=8, unique=True)
    closed_date = models.DateField()
    opening_ref = models.CharField(max_length=8, unique=True)
    opening_date = models.DateField()
    market = models.CharField(max_length=255)
    period = models.CharField(max_length=8)
    direction = models.CharField(max_length=4)
    size = models.FloatField()
    opening_price = models.FloatField()
    closing_price = models.FloatField()
    trade_ccy = models.CharField(max_length=3)
    gross_profit = models.FloatField()
    funding = models.FloatField()
    borrowing = models.FloatField()
    dividends = models.FloatField()
    lrprem = models.FloatField()
    others = models.FloatField()
    commccy = models.FloatField()
    comm = models.FloatField()
    net_profit = models.FloatField()
    def __str__(self):
        return '%s %s' % (self.opening_ref, self.opening_date)
    class Meta:
        verbose_name = "IG Profit and Loss Entry"
        verbose_name_plural = "IG Profit and Loss Entries"


class Member(models.Model):
    user = models.OneToOneField(User, editable=True, unique=True)
    current_trade_size = models.FloatField()
    current_commission = models.FloatField()
    current_fun_fund =  models.FloatField()
    def __str__(self):
        return '%s' % (self.user.email)

class IndividualPL(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    igpl = models.ForeignKey(IGPL, on_delete=models.CASCADE)
    size = models.FloatField()
    commission = models.FloatField()
    fun_fund = models.FloatField()

    @property
    def net_profit(self):
        return self.igpl.net_profit * self.size / self.igpl.size

    @property
    def gross_profit(self):
        return self.igpl.gross_profit * self.size / self.igpl.size

    def __str__(self):
        return '%s %s %s' % (self.member.user.email, self.igpl.opening_date, self.igpl.market)
    class Meta:
        verbose_name = "Individual Profit and Loss Entry"
        verbose_name_plural = "Individual Profit and Loss Entries"


class IndividualCash(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    size = models.FloatField()
    transaction_date = models.DateTimeField('date published')
    def __str__(self):
        return '%s %s' % (self.member, self.transaction_date)
    class Meta:
        verbose_name = "Individual Cash Entry"
        verbose_name_plural = "Individual Cash Entries"
