import uuid

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from utils import utils
from utils.modelOperation import decodeJwtToken
from utils.result import Result
from utils.oss2Utils import OSS2Utils


# Create your views here.

@csrf_exempt
def editUserInfo(request):
    # 更新除了头像以外的所有信息
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

    user_name = request.POST.get('username')
    user_gender = request.POST.get('gender')
    user_birthday = request.POST.get('birthday')
    user_region = request.POST.get('region')
    user_introduction = request.POST.get('introduction')

    if user_name is not None and user_name != '':
        ordinary_user.username = user_name

    if user_gender is not None:
        ordinary_user.gender = user_gender

    if user_birthday is not None:
        ordinary_user.birthday = user_birthday

    if user_region is not None and user_region != '':
        ordinary_user.region = user_region

    if user_introduction is not None and user_introduction != '':
        ordinary_user.introduction = user_introduction

    ordinary_user.save()

    return JsonResponse(Result.success())


@csrf_exempt
def editUserProfilePicture(request):
    if request.method != 'POST':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, POST only'.format(request.method)
        ))

    encode_jwt = request.POST.get('encode_jwt')
    user_profile_photo = request.FILES.get('profile_photo')

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

    # 获取图片的扩展名
    file_extension = utils.checkFileExtension(
        filename=user_profile_photo.name,
        allowed_extensions=['.jpg', '.jpeg', '.png'],
    )

    # 如果扩展名检验失败
    if file_extension is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='invalid file extension',
        ))

    # 生成uuid
    oss_filename = uuid.uuid4().hex + file_extension

    # 调用云服务上传图片
    upload_url = OSS2Utils.upload(
        request_file=user_profile_photo,
        oss_filename=oss_filename,
        oss_folder=['user', 'profilePhoto']
    )

    if upload_url is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_INTERNAL_SERVER_ERROR,
            message='upload file failed',
        ))

    ordinary_user.profile_picture_url = upload_url

    ordinary_user.save()

    return JsonResponse(Result.success())


def queryUser(request):

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

    user_info = {
        'username': ordinary_user.username,
        'email': ordinary_user.email,
        'phone': ordinary_user.phone,

        'profile_picture_url': ordinary_user.profile_picture_url,
        'gender': ordinary_user.gender,
        'birthday': ordinary_user.birthday,
        'region': ordinary_user.region,
        'introduction': ordinary_user.introduction,

        'create_time': ordinary_user.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        'update_time': ordinary_user.update_time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    return JsonResponse(Result.success(user_info))


