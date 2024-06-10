import uuid

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from utils.modelOperation import decodeJwtToken
from utils.result import Result
from musicplayer import models


@csrf_exempt
def sendMessage(request):
    if request.method != 'POST':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, POST only'.format(request.method)
        ))

    encode_jwt = request.POST.get('encode_jwt')

    # 没有 jwt 令牌字段
    if encode_jwt is None or encode_jwt == '':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='no jwt token',
        ))

    ordinary_user = decodeJwtToken(encode_jwt)

    # jwt 令牌解析失败
    if ordinary_user is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='invalid jwt token',
        ))

    receiver_uid = request.POST.get('receiver_uid')
    receiver = models.OrdinaryUser.objects.filter(uid=receiver_uid).first()

    if receiver is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='receiver is not exist',
        ))

    if ordinary_user.uid == receiver.uid:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='cannot send message to yourself',
        ))

    message = request.POST.get('message')

    new_message = models.Message.objects.create(
        sender=ordinary_user,
        receiver=receiver,
        is_system_message=False,
        has_read=False,
        message=message,
    )

    return JsonResponse(Result.success())


@csrf_exempt
def getSystemMessage(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    encode_jwt = request.GET.get('encode_jwt')

    # 没有 jwt 令牌字段
    if encode_jwt is None or encode_jwt == '':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='no jwt token',
        ))

    ordinary_user = decodeJwtToken(encode_jwt)

    # jwt 令牌解析失败
    if ordinary_user is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='invalid jwt token',
        ))

    message_list = models.Message.objects.filter(
        receiver=ordinary_user,
        is_system_message=True,
    ).order_by('has_read', '-send_time').all()

    for message in message_list:
        message.has_read = True
        message.save()

    return JsonResponse(Result.success(
        [
            {
                'has_read': message_iterator.has_read,
                'message': message_iterator.message,
                'send_time': message_iterator.send_time.strftime('%Y-%m-%d %H:%M:%S'),
            }

            for message_iterator in message_list
        ]
    ))


@csrf_exempt
def getUserMessage(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    encode_jwt = request.GET.get('encode_jwt')

    # 没有 jwt 令牌字段
    if encode_jwt is None or encode_jwt == '':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='no jwt token',
        ))

    ordinary_user = decodeJwtToken(encode_jwt)

    # jwt 令牌解析失败
    if ordinary_user is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='invalid jwt token',
        ))

    message_list = models.Message.objects.filter(
        receiver=ordinary_user,
        is_system_message=False,
    ).order_by('has_read', '-send_time').all()

    data_return = [
        {
            'sender': {
                'uid': message_iterator.sender.uid,
                'username': message_iterator.sender.username,
                'profile_picture': message_iterator.sender.profile_picture_url,
            },
            'has_read': message_iterator.has_read,
            'message': message_iterator.message,
            'send_time': message_iterator.send_time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        for message_iterator in message_list
    ]

    for message in message_list:
        message.has_read = True
        message.save()

    return JsonResponse(Result.success(
        data_return
    ))
