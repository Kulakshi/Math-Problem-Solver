# Create your views here. - business logic

from django.shortcuts import render
from .forms import ProbForm

from userPortal.Services import Main
from userPortal.Services import regex_based_solver

from django.http import HttpResponse


def form(request):
    return HttpResponse("You successfully submitted the form")


def index(request):
    if request.method == 'POST':
        form = ProbForm(request.POST)
        message = 'No message'
        if form.is_valid():
            info = form.cleaned_data.get('info')
            ques = form.cleaned_data.get('question')
            info_type = form.cleaned_data.get('info_type')
            ques_type = form.cleaned_data.get('ques_type')
            use_ml = form.cleaned_data.get('use_ml')
            if(use_ml == 'True'):
                message = Main.handle({'info_type': info_type, 'info': info, 'ques_type': ques_type, 'ques': ques})
            else:
                message = regex_based_solver.handle({'info_type': info_type, 'info': info, 'ques_type': ques_type, 'ques': ques})

    else:
        form = ProbForm()
        message = ""

    return render(request, 'userPortal/index.html', {'form': form, 'message': message})
