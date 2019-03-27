# Create your views here. - business logic

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.http import JsonResponse
from .forms import NameForm

from userPortal.Services import Main
from userPortal.Services import regex_based_solver

from django.http import HttpResponse

def name(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['your_name']
            return HttpResponseRedirect('/thanks/', RequestContext(request))
        else:
            form = NameForm()
        return render(request, 'contact.html')


def form(request):
    return HttpResponse("You successfully submitted the form")


def index(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        message = 'No message'
        if form.is_valid():
            info = form.cleaned_data.get('your_name')
            ques = form.cleaned_data.get('question')
            info_type = form.cleaned_data.get('info_type')
            ques_type = form.cleaned_data.get('ques_type')
            use_ml = form.cleaned_data.get('use_ml')
            # message = services.test_from_file()
            if(use_ml):
                message = Main.handle({'info_type': info_type, 'info': info, 'ques_type': ques_type, 'ques': ques})
            else:
                message = regex_based_solver.handle({'info_type': info_type, 'info': info, 'ques_type': ques_type, 'ques': ques})

    else:
        form = NameForm()
        message = ""

    return render(request, 'userPortal/index.html', {'form': form, 'message': message})
