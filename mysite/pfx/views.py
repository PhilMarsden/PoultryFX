from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader
from django.contrib.auth.decorators import login_required
from pfx.models import Member,total_fun_fund
from pfx.ig.rest import ig_rest

from .models import IGPL,IndividualPL,IndividualCash

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


@login_required
def ig_view(request):
    if ig_rest.need_password():
        if request.method == 'POST':
            #print("Password form posted")
            #print (request.POST['password'])
            # create a form instance and populate it with data from the request:
            ig_rest.set_password(request.POST['password'])
            ig_rest.login()
            if ig_rest.need_password():
                #print("Password form posted - failed to login")
                template = loader.get_template('pfx/ig_get_password.html')
                context = {'identifier': ig_rest.get_identifier(),
                         }
                return HttpResponse(template.render(context, request))
            else:
                #print("Password form posted - Logged in to IG")
                return HttpResponseRedirect('/pfx/ig_view/')
        else:
            template = loader.get_template('pfx/ig_get_password.html')
            context = {'identifier': ig_rest.get_identifier(),
                       }
            return HttpResponse(template.render(context, request))

    else:
        if ig_rest.need_login():
            ig_rest.login()
            if ig_rest.need_password():
                #print("Password form posted - failed to login")
                template = loader.get_template('pfx/ig_get_password.html')
                context = {'identifier': ig_rest.get_identifier(),
                         }
                return HttpResponse(template.render(context, request))

        template = loader.get_template('pfx/ig_view.html')
        positions = ig_rest.get_positions()
        activities = ig_rest.get_activity()
        context = {'positions':positions, 'activities':activities}
        return HttpResponse(template.render(context, request))



