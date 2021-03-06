from django.contrib.auth.models import User
from ..models import UserProfile
from ..models import Expertise
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponseNotFound
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import filters
from .serializer import UserSerializer
from .serializer import LoginSerializer
from .serializer import TokenSerializer
from .serializer import SetProfileSerializer
from .serializer import GetUserListSerializer
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend

##--------------------API-------------------##
success_message = 'Success'
error_message = 'Error'

def ParseErrorMsg(msg):
    print(msg)
    for k in msg.keys():
        key = k
        break
    return msg[key][0]

@api_view(['POST'])
def UserCreate(request, format='json'):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        if user:
            json = {'msg':success_message}
            return Response(json)
    json = {      
            "msg": error_message,
            "errorMsg": ParseErrorMsg(serializer.errors)
            }
    return Response(json)

@api_view(['POST'])
def UserDelete(request, format='json'):
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        token_key = serializer.data['key']
        token = Token.objects.get(key=token_key)
        user = User.objects.get(id=token.user_id)
        user.delete()
        json = {'msg':success_message}
        return Response(json)
    json = {'msg':serializer.errors}
    return Response(json)



@api_view(['POST'])
def UserLogin(request, format='json'):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.data['username']
        password = serializer.data['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            if not Token.objects.filter(user_id__exact=user.id):
                token = Token.objects.create(user=user)
            else:
                token = Token.objects.get(user_id=user.id)
            json = {'msg':success_message, 'key':token.key}
            return Response(json)
    json = {
            "msg": error_message,
            "errorMsg": ParseErrorMsg(serializer.errors)
            }
    return Response(json)

@api_view(['POST'])
def GetProfile(request, format='json'):
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        token_key = serializer.data['key']
        token = Token.objects.get(key=token_key)
        user = User.objects.get(id=token.user_id)
        profile = UserProfile.objects.get(user_id=token.user_id)
        exps = []
        for exp in profile.expertises.all():
            exps.append(exp.expertise)
        json = {
                'msg': success_message, 
                'username': user.username, 
                'email':user.email, 
                'expertise':exps
                }
        return Response(json)
    
    json = {'msg':serializer.errors}       
    return Response(json)

@api_view(['POST'])
def SetProfile(request, format='json'):
    token_serializer = TokenSerializer(data=request.data)
    profile_serializer = SetProfileSerializer(data=request.data)
    if token_serializer.is_valid():
        token_key = token_serializer.data['key']
        token = Token.objects.get(key=token_key)
        if profile_serializer.is_valid():
            expertise_str = profile_serializer.data['expertises']
            profile = UserProfile.objects.get(user_id=token.user_id)
            profile.expertises.clear()
            for exp in expertise_str:
                exper = Expertise(expertise=exp)
                exper.save()
                profile.save()
                profile.expertises.add(exper)
            #exps = []
            #for exp in profile.expertises.all():
            #     exps.append(exp.expertise)
            json = {'msg': success_message} #, 'expertise':exps}
            return Response(json)
    json = {'msg':token_serializer.errors+profile_serializer.errors}
    return Response(json)

class GetUserList(generics.ListAPIView):
    serializer_class = GetUserListSerializer
    lookup_url_kwarg = "username"
    #filter_backends = (DjangoFilterBackend,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username')
    def get_queryset(self):
        queryset = User.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            return queryset.filter(username__contains=username)
            
        else:
            return queryset
