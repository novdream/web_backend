from django.core.mail import EmailMessage

from django.core.mail import send_mail

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from utils.result import Result

import utils.utils as utils
import utils.modelCheck as modelCheck
import utils.modelOperation as modelOperation
from musicplayer import models


# Create your views here.

# def testEmail(request):
#     email = EmailMessage(
#         'Test Subject',
#         'Test Message',
#
#         from_email='yulo25541733@163.com',
#         to=['2152813@tongji.edu.cn']
#     )
#     email.send()
#
#     message_dict = {'code': 200, 'message': 'success', 'obj': None}
#     return JsonResponse(message_dict)


def existEmail(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    user_email = request.GET.get('user_email')

    if utils.checkEmail(user_email):
        return JsonResponse(Result.success(
            modelCheck.existEmailCheck(user_email))
        )
    else:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_BAD_REQUEST,
            message='Illegal Email Format'
        ))


def existUserName(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    userName = request.GET.get('user_name')

    return JsonResponse(Result.success(
        modelCheck.existUserCheck(userName)
    ))


def generateCaptcha(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    user_email = request.GET.get('user_email')

    # 邮箱的格式不合法
    if not utils.checkEmail(user_email):
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_BAD_REQUEST,
            message='Illegal Email Format'
        ))

    # 这里允许邮箱重复
    # X邮箱已经被使用X
    # if modelCheck.existEmailCheck(user_email):
    #     return JsonResponse(Result.failure(
    #         code=Result.HTTP_STATUS_CONFLICT,
    #         message='Email {} has been registered'.format(user_email)
    #     ))

    # 生成验证码
    captcha_text = utils.generateCaptcha()

    # 将验证码和用户邮箱保存到Session中
    # request.session['captcha'] = captcha_text
    # request.session['user_email'] = user_email

    # 将验证码和用户邮箱保存到数据库中
    record = models.Captcha.objects.filter(
        user_email=user_email
    ).first()

    if record is None:
        record = models.Captcha.objects.create(
            user_email=user_email
        )

    record.captcha = captcha_text
    record.expire_time = timezone.now() + timezone.timedelta(minutes=30)

    record.save()

    # 向目标邮箱发送验证码
    # EmailMessage(
    #     subject='音乐播放器验证',
    #     body='欢迎您使用音乐播放器，您的验证码是{},请尽快进行验证'.format(captcha_text),
    #     from_email='yulo25541733@163.com',
    #     to=[user_email]
    # ).send()

    send_mail(
        subject='音乐播放器验证',
        message='欢迎您使用音乐播放器，您的验证码是{},请尽快进行验证'.format(captcha_text),
        from_email='yulo25541733@163.com',
        recipient_list=[user_email]
    )

    return JsonResponse(Result.success())


@csrf_exempt
def userRegister(request):
    if request.method != 'POST':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, POST only'.format(request.method)
        ))

    username = request.POST.get('user_name')
    password = request.POST.get('user_password')
    user_email = request.POST.get('user_email')
    captcha = request.POST.get('captcha')

    # 校验会话中是否存在验证码
    record = models.Captcha.objects.filter(
        user_email=user_email,
        captcha=captcha,
        expire_time__gt=timezone.now()
    ).first()

    # 校验会话的验证码是否与表单提交的验证码一致
    if record is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='Captcha check failed'
        ))

    record.delete()

    # 校验密码
    if not utils.checkPassword(password):
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='Password check failed'
        ))

    # 校验邮箱是否唯一 这里不用校验邮箱是否合法，因为发送邮件时校验过了
    if modelCheck.existEmailCheck(email_str=user_email):
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_CONFLICT,
            message='Email has been registered'
        ))

    # 用户信息保存到数据库
    new_user = models.OrdinaryUser.objects.create(
        username=username,
        email=user_email,
        password=password,
    )

    # 生成jwt令牌
    encode_jwt = modelOperation.generateJwtToken(new_user)

    # 将令牌写入会话中
    # request.session['jwt_token'] = encode_jwt

    return JsonResponse(Result.success(encode_jwt))


@csrf_exempt
def userLogin(request):
    if request.method != 'POST':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, POST only'.format(request.method)
        ))

    user_email = request.POST.get('user_email')
    user_password = request.POST.get('user_password')

    # 利用邮箱和密码进行匹配
    user_obj = modelCheck.checkUserLogin(user_email, user_password)

    # 邮箱和密码不匹配
    if user_obj is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='Email or Password is incorrect'
        ))

    # 生成jwt令牌
    encode_jwt = modelOperation.generateJwtToken(user_obj)

    return JsonResponse(Result.success(encode_jwt))


@csrf_exempt
def userModifyPassword(request):
    if request.method != 'POST':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, POST only'.format(request.method)
        ))

    user_email = request.POST.get('user_email')
    user_password_new = request.POST.get('user_password_new')
    user_password_old = request.POST.get('user_password_old')
    user_captcha = request.POST.get('captcha')

    # 获取验证码，删除会话中的邮箱和验证码字段
    session_captcha = request.session['captcha']
    session_user_email = request.session['user_email']
    request.session.delete('captcha')
    request.session.delete('user_email')

    # 校验新密码是否合法
    if not utils.checkPassword(user_password_new):
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='Password check failed'
        ))

    # 校验会话的验证码是否与表单提交的验证码一致
    if session_captcha != user_captcha or session_user_email != user_email:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='Captcha check failed'
        ))

    # 查询用户信息
    ordinary_user = models.OrdinaryUser.objects.filter(
        email=user_email,
        password=user_password_old,
    ).first()

    # 没有找到该用户
    if ordinary_user is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='No such user in database',
        ))

    ordinary_user.password = user_password_new
    ordinary_user.save()

    return JsonResponse(Result.success())


def checkJwtToken(request):
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

    ordinary_user = modelOperation.decodeJwtToken(encode_jwt)

    # jwt 令牌解析失败
    if ordinary_user is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='invalid jwt token',
        ))

    return JsonResponse(Result.success())


def updateJwtToken(request):
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

    ordinary_user = modelOperation.decodeJwtToken(encode_jwt)

    # jwt 令牌解析失败
    if ordinary_user is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='invalid jwt token',
        ))

    new_jwt_token = modelOperation.generateJwtToken(ordinary_user, 2)

    return JsonResponse(Result.success(new_jwt_token))
