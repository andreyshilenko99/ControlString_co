from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.

def export(request):
    response = str(request.POST)
    new = response[:len(response) - 9]
    newnew = new[14:]
    with open('serv/static/data.jsonp', 'w') as outfile:
        outfile.write(newnew)
    print(newnew)

    return HttpResponse('test.html')