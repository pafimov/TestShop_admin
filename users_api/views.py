from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import User
from rest_framework.parsers import JSONParser 
from .serializers import UserSerializer
from rest_framework import status

# Create your views here.
@api_view(['GET'])
def index(request):
    users = User.objects.all()
    return JsonResponse([{'len': len(users)}, [1, 2]], safe=0)

@api_view(['POST'])
def add_user(request):
    data = JSONParser().parse(request)
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_user(request):
    data = JSONParser().parse(request)
    if not 'id' in data or not 'sum' in data:
        return JsonResponse({'success' : '0'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(telegram_id = data['id'])
    except User.DoesNotExist:
        return JsonResponse({'success' : '0'}, status=status.HTTP_400_BAD_REQUEST)
    user.sum_bought += data['sum']
    user.save()
    return JsonResponse({'success' : '1'})
