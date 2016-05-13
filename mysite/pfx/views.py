from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader
from django.contrib.auth.decorators import login_required
from pfx.models import Member,total_fun_fund,total_cash,total_gross_profit,total_commission
from pfx.ig.rest import ig_rest

from .models import IGPL,IndividualPL,IndividualCash

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
logger.info('Views Initialised')


@login_required
def profile(request):
    m = Member.objects.get(user = request.user)
    trades = IndividualPL.objects.filter(member = m)
    positions = ig_rest.get_positions(member = m)
    fun_fund = -total_fun_fund()
    template = loader.get_template('pfx/profile.html')
    context = {
        'trades': trades,
        'member' : m,
        'positions': positions,
        'fun_fund' : fun_fund
    }
    return HttpResponse(template.render(context, request))


def ig_base(request,redirect_url):
    logger.debug('Check IG Login')
    if ig_rest.need_password():
        logger.debug('Password needed')
        if request.method == 'POST':
            logger.debug('Password posted, try IG Login')
            ig_rest.set_password(request.POST['password'])
            ig_rest.login()
            if ig_rest.need_password():
                logger.warn('Password form posted - failed IG Login')
                template = loader.get_template('pfx/ig_get_password.html')
                context = {'identifier': ig_rest.get_identifier(),
                           }
                return HttpResponse(template.render(context, request))
            else:
                logger.info('Password form posted - IG Login succeeded')

                return HttpResponseRedirect(redirect_url)
        else:
            template = loader.get_template('pfx/ig_get_password.html')
            context = {'identifier': ig_rest.get_identifier(),
                       }
            return HttpResponse(template.render(context, request))
    else:
        logger.debug('Password set')
        if ig_rest.need_login():
            logger.debug('Login needed')
            ig_rest.login()
            if ig_rest.need_password():
                logger.warn('IG Login failed')
                # print("Password form posted - failed to login")
                template = loader.get_template('pfx/ig_get_password.html')
                context = {'identifier': ig_rest.get_identifier(),
                           }
                return HttpResponse(template.render(context, request))

    return None


@login_required
def ig_trades(request):
   retval = ig_base(request,'/pfx/ig_trades/')
   if (retval != None):
       return retval

   template = loader.get_template('pfx/ig_view.html')
   trades = IGPL.objects.all()
   context = {'trades':trades, 'show_trades':True}
   return HttpResponse(template.render(context, request))


@login_required
def ig_positions(request):
   retval = ig_base(request,'/pfx/ig_positions/')
   if (retval != None):
       return retval

   template = loader.get_template('pfx/ig_view.html')
   positions = ig_rest.get_positions()
   context = {'positions':positions, 'show_positions':True}
   return HttpResponse(template.render(context, request))

@login_required
def ig_activities(request):
   retval = ig_base(request,'/pfx/ig_activities/')
   if (retval != None):
       return retval

   template = loader.get_template('pfx/ig_view.html')
   activities = ig_rest.get_activity()
   context = {'activities':activities, 'show_activities':True}
   return HttpResponse(template.render(context, request))


@login_required
def members(request):
   template = loader.get_template('pfx/members.html')
   members = Member.objects.all()
   context = {'members':members,
              'total_cash_deposit': total_cash(),
              'total_gross_profit':total_gross_profit(),
              'total_fun_fund':-total_fun_fund(),
              'total_deductions':total_commission() + total_fun_fund(),
              'total_commission':-total_commission(),
              'total_net_profit':total_gross_profit() + total_commission() + total_fun_fund(),
              'total_balance':total_cash() + total_gross_profit() + total_commission() + total_fun_fund(),
              'total_ig_balance':total_cash() + total_gross_profit()}
   return HttpResponse(template.render(context, request))


