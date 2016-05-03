from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib.humanize.templatetags.humanize import intcomma

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

    def save(self, *args, **kwargs):
        super(IGPL, self).save(*args, **kwargs) # Call the "real" save() method.
        member_list = Member.objects.all()
        for m1 in member_list:
            ipl1 = IndividualPL(member=m1, igpl=self)
            ipl1.save()

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
    @property
    def name(self):
        return self.user.get_full_name()

    @property
    def cash_deposit(self):
        return IndividualCash.objects.filter(member_id=self.id).aggregate(Sum('size')).get('size__sum', 0.00)

    @property
    def profit(self):
        return IndividualPL.objects.filter(member_id=self.id).aggregate(Sum('profit')).get('profit__sum', 0.00) + self.deductions

    @property
    def deductions(self):
         return IndividualPL.objects.filter(member_id=self.id).aggregate(Sum('commission')).get('commission__sum', 0.00) + \
                IndividualPL.objects.filter(member_id=self.id).aggregate(Sum('fun_fund')).get('fun_fund__sum', 0.00)

    @property
    def balance(self):
        return self.cash_deposit + self.profit

    def __str__(self):
        return '%s' % (self.user.email)

class IndividualPL(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    igpl = models.ForeignKey(IGPL, on_delete=models.CASCADE)
    size = models.FloatField(default=0)
    profit = models.FloatField(default=0)
    commission = models.FloatField(default=0)
    fun_fund = models.FloatField(default=0)

    @property
    def deductions(self):
        return  (self.commission + self.fun_fund)

    @property
    def net_profit(self):
        return self.profit + self.deductions

    #def default_profit(self):
    #    return 1.0

    def save(self, *args, **kwargs):
        self.size = self.igpl.size * self.member.current_trade_size / Member.objects.all().aggregate(Sum('current_trade_size')).get('current_trade_size__sum',0.00)
        self.profit = self.igpl.net_profit * self.member.current_trade_size / Member.objects.all().aggregate(Sum('current_trade_size')).get('current_trade_size__sum',0.00)
        self.fun_fund = - max(self.profit * self.member.current_fun_fund,0.0)
        self.commission = - max(self.profit * self.member.current_commission,0.0)
        super(IndividualPL, self).save(*args, **kwargs) # Call the "real" save() method.

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
