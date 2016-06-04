from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader
from django.contrib.auth.decorators import login_required,permission_required
from pfx.models import Member,total_fun_fund,total_cash,total_gross_profit,total_commission,total_calculated_trade_size,total_net_profit,total_return
from pfx.ig.rest import ig_rest,ig_activity
from pfx.ig.imap import pfx_imap

from .models import IGPL,IndividualPL,IndividualCash

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
logger.info('Views Initialised')


@login_required
def profile(request):
    m = Member.objects.get(user = request.user)
    trades = IndividualPL.objects.filter(member = m).order_by('-igpl__closed_date')
    positions = ig_rest.get_positions(member = m)
    fun_fund = -total_fun_fund()
    template = loader.get_template('pfx/profile.html')
    context = {
        'trades': trades,
        'member' : m,
        'positions': positions,
        'fun_fund' : fun_fund
    }
    if len(trades) != 0:
        logger.debug("Auto refresh = True")
        context['autorefresh'] = True

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
   trades = IGPL.objects.all().order_by('-closed_date')
   context = {'trades':trades, 'show_trades':True, 'show_positions':False, 'show_activities':False}
   return HttpResponse(template.render(context, request))


@login_required
def ig_positions(request):
   retval = ig_base(request,'/pfx/ig_positions/')
   if (retval != None):
       return retval

   template = loader.get_template('pfx/ig_view.html')
   positions = ig_rest.get_positions()
   context = {'positions':positions, 'show_positions':True, 'show_trades':False, 'show_activities':False }
   return HttpResponse(template.render(context, request))

@login_required
def ig_activities(request):
   retval = ig_base(request,'/pfx/ig_activities/')
   if (retval != None):
       return retval

   if 'dealid' in request.GET:
       deal_id_to_add = request.GET['dealid']
       logger.debug('Deal id {} to be added as trade'.format(deal_id_to_add))
       act = ig_activity.get_act(deal_id_to_add)
       if (act == None):
            logger.debug('Cannot find deal id {}'.format(deal_id_to_add))
       else:
            logger.debug('Adding trade for deal id {}'.format(deal_id_to_add))
            l_igpl = act.add_trade(True)
   if 'dealid_phil' in request.GET:
       deal_id_to_add = request.GET['dealid_phil']
       logger.debug('Deal id {} to be added as trade for Phil'.format(deal_id_to_add))
       act = ig_activity.get_act(deal_id_to_add)
       if (act == None):
           logger.debug('Cannot find deal id {}'.format(deal_id_to_add))
       else:
           logger.debug('Adding trade for deal id {}'.format(deal_id_to_add))
           l_igpl = act.add_trade(False)
           l_igpl.AddPhilIndividualPL()
   template = loader.get_template('pfx/ig_view.html')
   activities = ig_rest.get_activity(include_all=False)
   context = {'activities':activities, 'show_activities':True, 'show_positions':False, 'show_trades':False }
   return HttpResponse(template.render(context, request))


@permission_required('is_superuser')
def members(request):
   if 'id' in request.GET:
       m = Member.objects.get(id = request.GET['id'])
       trades = IndividualPL.objects.filter(member=m).order_by('-igpl__closed_date')
       positions = ig_rest.get_positions(member=m)
       fun_fund = -total_fun_fund()
       template = loader.get_template('pfx/profile.html')
       context = {
          'trades': trades,
          'member': m,
          'positions': positions,
          'fun_fund': fun_fund
       }
   else:
       if 'updatetradesizes' in request.GET:
           logger.info("Updating trade sizes")
           percent = int(request.GET['percent'])
           points = int(request.GET['points'])
           logger.debug('Updating trades for percent = {} points = {}'.format(percent,points))
           Member.set_all_trade_sizes(percent,points)

       template = loader.get_template('pfx/members.html')
       members = Member.objects.all()
       context = {'members':members,
                  'total_calculated_trade_size': total_calculated_trade_size(),
                  'total_cash_deposit': total_cash(),
                  'total_gross_profit':total_gross_profit(),
                  'total_fun_fund':-total_fun_fund(),
                  'total_deductions':total_commission() + total_fun_fund(),
                  'total_commission':-total_commission(),
                  'total_net_profit':total_net_profit(),
                  'total_balance':total_cash() + total_gross_profit() + total_commission() + total_fun_fund(),
                  'total_return':100 * (total_return()),
                  'total_ig_balance':total_cash() + total_gross_profit()}

   return HttpResponse(template.render(context, request))


