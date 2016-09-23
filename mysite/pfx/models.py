from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib.humanize.templatetags.humanize import intcomma

# Get an instance of a logger
import logging
logger = logging.getLogger(__name__)
print("enable logging " + __name__)
logger.info('Models Initialised')

class PositionViews(models.Model):
    deal_id = models.CharField(max_length=255, unique=True)
    show_all = models.BooleanField(default=False)
    class Meta:
        verbose_name = "Position View"
        verbose_name_plural = "Position Views"
    def __str__(self):
        return '%s Show All : %s' % (self.deal_id,self.show_all)


class TradeEmail(models.Model):
    message_id = models.CharField(max_length=255)
    trade_date = models.CharField(max_length=32)
    time_live = models.CharField(max_length=32)
    market = models.CharField(max_length=255)
    start_price = models.FloatField()
    stop_price = models.FloatField()
    target_price = models.FloatField()

    def __str__(self):
        return '%s %s' % (self.market,self.trade_date)
    class Meta:
        verbose_name = "Trade Email"
        verbose_name_plural = "Trade Emails"



class IGPL(models.Model):
    closing_ref = models.CharField(max_length=8, unique=True)
    closed_date = models.DateField()
    opening_ref = models.CharField(max_length=8)
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

    def AddIndividualPL(self,m1,member_list):
        IndividualPL.AddNewCalculatedEntry(m1, self, member_list)

    def AddAllIndividualPL(self):
        member_list = Member.objects.all()
        for m1 in member_list:
            self.AddIndividualPL(m1,member_list)

    def AddPhilIndividualPL(self):
        u1 = User.objects.get(email='phil.marsden@softwire.com')
        member_list = Member.objects.filter(user=u1)
        for m1 in member_list:
            cc = m1.current_commission
            cf = m1.current_fun_fund
            m1.current_commission = 0.0
            m1.current_fun_fund = 0.0
            m1.save()
            self.AddIndividualPL(m1,member_list)
            m1.current_commission = cc
            m1.current_fun_fund = cf
            m1.save()

    def save(self, *args, **kwargs):
        super(IGPL, self).save(*args, **kwargs) # Call the "real" save() method.

    def __str__(self):
        return '%s %s' % (self.opening_ref, self.opening_date)
    class Meta:
        verbose_name = "IG Profit and Loss Entry"
        verbose_name_plural = "IG Profit and Loss Entries"


class Member(models.Model):
    user = models.OneToOneField(User, editable=True, unique=True)
    manual_trade_size = models.FloatField()
    calculated_trade_size = models.FloatField(default = 0)
    current_commission = models.FloatField()
    current_fun_fund =  models.FloatField()
    automatic_trade_size = models.BooleanField(default=False)
    commission_received = models.FloatField(default = 0.0)

    @staticmethod
    def set_all_trade_sizes(percent,points):
        member_list = Member.objects.all()
        for m1 in member_list:
            m1.set_calculated_trade_size(percent,points)

    @staticmethod
    def set_all_trade_sizes_old():
        member_list = Member.objects.all()
        for m1 in member_list:
            m1.set_calculated_trade_size_old()

    @property
    def name(self):
        return self.user.get_full_name()

    def set_calculated_trade_size(self,percent,points):
        if (self.automatic_trade_size):
            risk_per_trade = self.balance * percent / 100
            pounds_per_point = risk_per_trade / points
            self.calculated_trade_size = round((pounds_per_point - 0.5),0)
        else:
            self.calculated_trade_size = self.manual_trade_size
        self.save()

    def set_calculated_trade_size_old(self):
        if (self.automatic_trade_size):
            self.calculated_trade_size = round((self.balance - 150.0) /300, 0)
        else:
            self.calculated_trade_size = self.manual_trade_size
        self.save()

    def percentage_of_trades(self, all_members):
        sum_tsize = 0
        for m in all_members:
            sum_tsize += m.calculated_trade_size
        return (self.calculated_trade_size / sum_tsize)

    @property
    def trades_return_percentage(self):
        trades = IndividualPL.objects.filter(member=self).order_by('igpl__closed_date')
        l_return = 1.0
        for t in trades:
            logger.debug('Trade percentage = {}'.format(t.return_percentage ))
            l_return = t.return_percentage * l_return
            logger.debug('Cummulative Return percentage = {}'.format(l_return))

        logger.debug('Return percentage = {}'.format(l_return))
        return (l_return - 1.0) * 100.0

    @property
    def actual_return_percentage(self):
        increase = self.net_profit + self.commission_received_pounds
        return 100 * increase / (self.cash_deposit)

    @property
    def cash_deposit(self):
        tcash = IndividualCash.objects.filter(member_id=self.id).aggregate(Sum('size')).get('size__sum', 0.00)
        return 0 if tcash == None else tcash

    @property
    def gross_profit(self):
        tgross = IndividualPL.objects.filter(member_id=self.id).aggregate(Sum('profit')).get('profit__sum',0.00)
        return 0 if tgross == None else tgross

    @property
    def net_profit(self):
        tprofit = IndividualPL.objects.filter(member_id=self.id).aggregate(Sum('profit')).get('profit__sum', 0.00)
        if tprofit == None:
            tprofit = 0
        return (tprofit + self.deductions)

    @property
    def commission_received_pounds(self):
        return self.commission_received * total_commission() * -1.0

    @property
    def deductions(self):
         tcomm = IndividualPL.objects.filter(member_id=self.id).aggregate(Sum('commission')).get('commission__sum', 0.00)
         if tcomm == None:
             tcomm = 0
         tfun = IndividualPL.objects.filter(member_id=self.id).aggregate(Sum('fun_fund')).get('fun_fund__sum', 0.00)
         if tfun == None:
             tfun = 0
         return  tcomm + tfun


    @property
    def balance(self):
        b = self.cash_deposit + self.net_profit + self.commission_received_pounds
        return b

    def __str__(self):
        return '%s' % (self.user.email)

class IndividualPL(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    igpl = models.ForeignKey(IGPL, on_delete=models.CASCADE)
    size = models.FloatField(default=0)
    profit = models.FloatField(default=0)
    commission = models.FloatField(default=0)
    fun_fund = models.FloatField(default=0)
    net_return = models.FloatField(default=0)

    @property
    def return_percentage(self):
        #return (self.net_profit + (self.size * 300)) / (self.size * 300)
        return self.net_return

    @property
    def return_percentage_display(self):
        return round((self.net_return - 1.0) * 100,4)

    @staticmethod
    def AddNewCalculatedEntry(m1, igpl1,all_members):
        ipl1 = IndividualPL(member=m1, igpl=igpl1)
        ipl1.size = igpl1.size * m1.percentage_of_trades(all_members)
        ipl1.profit = igpl1.net_profit * m1.percentage_of_trades(all_members)
        ipl1.fun_fund = - max(ipl1.profit * m1.current_fun_fund,0.0)
        ipl1.commission = - max(ipl1.profit * m1.current_commission,0.0)
        ipl1.net_return = 1.0 + ipl1.net_profit / m1.balance
        logger.info('Member {} trade of size {} with commission {} net return {} based on Profit:{} Commission:{}'.format(
                                                                                        ipl1.member,
                                                                                        ipl1.size,
                                                                                        ipl1.commission,
                                                                                        ipl1.net_return,
                                                                                        ipl1.profit,
                                                                                        ipl1.member.current_commission))

        ipl1.save()

        #f = open('tmp.txt', 'a')
        #f.write("assert (Member.objects.get(user=User.objects.get(email='{}')).calculated_trade_size == {})\n".format(ipl1.member, round(ipl1.size,0)))
        #f.write("assert (Member.objects.get(user=User.objects.get(email='{}')).balance == {})\n".format(ipl1.member,ipl1.member.balance))
        #f.close()

    @property
    def deductions(self):
        return  self.commission + self.fun_fund

    @property
    def net_profit(self):
        return self.profit + self.deductions

    #def default_profit(self):
    #    return 1.0

    def save(self, *args, **kwargs):
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
        return '%s %s %d' % (self.member, self.transaction_date, self.size)
    class Meta:
        verbose_name = "Individual Cash Entry"
        verbose_name_plural = "Individual Cash Entries"

class FunFundWithdrawl(models.Model):
    amount = models.FloatField()
    decription = models.CharField(max_length=255)
    transaction_date = models.DateTimeField('date published')
    def __str__(self):
        return '%s %d' % (self.transaction_date, self.amount)
    class Meta:
        verbose_name = "Fun fund withdrawl"
        verbose_name_plural = "Fun fund withdrawls"

def total_fun_fund():
    tfun = IndividualPL.objects.all().aggregate(Sum('fun_fund')).get('fun_fund__sum',0.00)
    if tfun == None:
        tfun = 0
    return tfun

def total_fun_fundw():
    tfunw = FunFundWithdrawl.objects.all().aggregate(Sum('amount')).get('amount__sum', 0.00)
    if tfunw == None:
        tfunw = 0
    return tfunw

def total_commission():
    tcom = IndividualPL.objects.all().aggregate(Sum('commission')).get('commission__sum',0.00)
    return 0 if tcom == None else tcom

def total_cash():
    tcash = IndividualCash.objects.all().aggregate(Sum('size')).get('size__sum', 0.00)
    return 0 if tcash == None else tcash

def total_net_profit():
    return total_gross_profit() + total_fun_fund() + total_commission()

def total_return():
    return total_net_profit() / (total_cash() + total_net_profit())

def total_calculated_trade_size():
    return Member.objects.all().aggregate(Sum('calculated_trade_size')).get('calculated_trade_size__sum', 0.00)

def total_gross_profit():
    p1 = round(IndividualPL.objects.all().aggregate(Sum('profit')).get('profit__sum',0.00),2)
    p2 = round(IGPL.objects.all().aggregate(Sum('net_profit')).get('net_profit__sum', 0.00),2)
    logger.info('Profit from individual trades = ' + str(p1))
    logger.info('Profit from trades = ' + str(p2))
    if (p1 != p2):
        logger.error('Profit from individual trades = ' + str(p1))
        logger.error('Profit from trades = ' + str(p2))
        logger.error('*** Profit mismatch ***')
        raise Exception("Profits mismatch")
    else:
        return p1

#tProfit = total_gross_profit()
#logger.info('Commission = £' + str(total_commission()))
#logger.info('Profit = £' + str(tProfit))
#logger.info('Cash = £' + str(total_cash()))
#logger.info('=========')
#logger.info('Total IG Balance = £' + str(tProfit +  total_cash()))
#logger.info('Fun fund = £' + str(total_fun_fund()))

