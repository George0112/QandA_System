from django.contrib.auth.models import User
from ..models import Expertise
from ..models import QuestionForm
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponseNotFound
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializer import QuestionSerializer
from .serializer import DeleteQuestionSerializer
from rest_framework.authtoken.models import Token


##--------------------API-------------------##
success_msg = 'Success'

@api_view(['POST'])
def PostQuestion(request, format='json'):
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        question = serializer.save()
        json = {
                "msg": success_msg, 
                "question_id": question.id
                }
        return Response(json, status=status.HTTP_200_OK)
    json = {"msg": serializer.errors}
    return Response(json, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def ModifyQuestion(request, format='json'):
    try: question_id = request.data['question_id']
    except: error_msg = 'No question_id or format is wrong'
    else:
        if QuestionForm.objects.filter(id__exact=question_id):
            question_instance = QuestionForm.objects.get(id=question_id)
            serializer = QuestionSerializer(question_instance, data=request.data, partial=True)
            if serializer.is_valid():
                question = serializer.save()
                json = {"msg": success_msg}
                return Response(json, status=status.HTTP_200_OK)
            else: error_msg = serializer.errors
        else: error_msg = 'This question_id does not exist.'
    json = {"msg": error_msg}
    return Response(json, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def DeleteQuestion(request, format='json'):
    serializer = DeleteQuestionSerializer(data=request.data)
    if serializer.is_valid():
        question_id = serializer.data['question_id']
        token = serializer.data['key']
        question = QuestionForm.objects.get(id=question_id)
        if Token.objects.get(key=token).user_id == question.user_id:
            question.delete()
            json = {"msg": success_msg}
            return Response(json, status=status.HTTP_200_OK)
        else: error_msg = 'The author of the question does not match the token.'
    else: error_msg = serializer.errors
    json = {"msg": error_msg}
    return Response(json, status=status.HTTP_400_BAD_REQUEST)


def GetQuestionByID(id):
    question = QuestionForm.objects.get(id=id)
    exps = []
    for exp in question.expertises.all():
        exps.append(exp.expertise)
    json = {
            "question_id": id,
            "username": question.user.username,
            "title": question.title,
            "content": question.content,
            "create_date": question.create_date,
            "modify_date": question.mod_date,
            "reply_number": question.reply_number,
            "expertises": exps,
            }
    return json

@api_view(['GET'])
def GetQuestion(request, pk):
    if pk == '0':
        quests = []
        for quest in QuestionForm.objects.all():
            quests.append({"question": GetQuestionByID(quest.id)})
        json = {
                "msg": success_msg,
                "questions": quests
                }
        return Response(json, status=status.HTTP_200_OK)
    else:
        if not QuestionForm.objects.filter(id=pk):
            error_msg = 'Wrong question id'
        else:
            json =GetQuestionByID(pk)
            return Response(json, status=status.HTTP_200_OK)
        json = {"msg": error_msg}
        return Response(json, status=status.HTTP_400_BAD_REQUEST)


