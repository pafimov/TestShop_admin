from io import StringIO
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import UserFree
from .serializers import UserFreeSerializer
from django.core.management import call_command
from .forms import MailingForm
from PIL import Image
import os

def mailing(request):
    if request.method == "POST":
        form = MailingForm(request.POST, request.FILES)
        if form.is_valid():
            text = form.cleaned_data.get("text")
            f = request.FILES['img']
            new_num = len(os.listdir("./pics"))+1
            path = './pics/' + str(new_num) + ".jpg"
            with open(path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            call_command('gomailing', path, text)
            return HttpResponse("OK")
    else:
        form = MailingForm()
    return render(request, "mailing.html", {"form" : form})
