from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
# Create your views here.
def hello_world(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())