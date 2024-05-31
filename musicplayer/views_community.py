import uuid

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from utils.modelOperation import decodeJwtToken
from utils.oss2Utils import OSS2Utils
from utils.result import Result
from utils import utils
from musicplayer import models, models_sqlview


# 创建社群
@csrf_exempt
def createCommunity(request):
    if request.method != 'POST':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, POST only'.format(request.method)
        ))

    data = request.POST
    cname = data.get('community_name')
    music_type = data.get('music_type')
    introduction = data.get('introduction')
    profile_picture = request.FILES.get('profile_picture')
    if cname is None or music_type is None or introduction is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_FOUND,
            message='unfilled information',
        ))
    # 获取图片的扩展名
    if profile_picture is not None:
        file_extension = utils.checkFileExtension(
            filename=profile_picture.name,
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
            request_file=profile_picture,
            oss_filename=oss_filename,
            oss_folder=['community', 'profilePhoto']
        )

        if upload_url is None:
            return JsonResponse(Result.failure(
                code=Result.HTTP_STATUS_INTERNAL_SERVER_ERROR,
                message='upload file failed',
            ))
    else:
        upload_url = None
    record = models.Community.objects.filter(cname=cname).count()
    # print(record)
    if record:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='exits the same community',
        ))

    community = models.Community.objects.create(
        cname=cname,
        profile_picture_url=upload_url,
        music_type=music_type,
        introduction=introduction
    )

    return JsonResponse(Result.success())


# 用户关注社群
@csrf_exempt
def UserFollowCommunity(request):
    if request.method != 'POST':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, POST only'.format(request.method)
        ))
    data = request.POST
    encode_jwt = data.get('encode_jwt')
    name = data.get('community_name')

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

    community = models.Community.objects.get(cname=name)
    if community is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='invalid community name',
        ))
    # print(community)
    record = models.UserFollowCommunity.objects.filter(ordinaryUser=ordinary_user, community=community).first()
    # print(record)
    if record is not None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='already followed community',
        ))

    models.UserFollowCommunity.objects.create(ordinaryUser=ordinary_user, community=community)
    return JsonResponse(Result.success())


# 展示用户前5评论最多的社群
def showTop5Community(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    encode_jwt = request.GET.get('encode_jwt')
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

    # 查看用户是否有创作者权限
    uid = ordinary_user.uid

    communities_ids = models.UserFollowCommunity.objects.filter(ordinaryUser=uid).values_list('community', flat=True)
    ids = list(communities_ids)
    communities = models.Community.objects.filter(id__in=ids).values_list('tube', type,
                                                                          flat=True)  # 使用 values_list 获取社群的名称列表
    print(communities)
    return JsonResponse(Result.success(
        {
            'ids': list(communities_ids),
        }
    ))


# 获取用户关注所有社群,按时间排序
def getUserAllCommunity(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    encode_jwt = request.GET.get('encode_jwt')
    # print(encode_jwt)
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

    followed_communities = models.UserFollowCommunity.objects.filter(
        ordinaryUser=ordinary_user
    ).values_list('community', 'follow_time')

    community_ids = [info[0] for info in followed_communities]
    followe_time = [info[1] for info in followed_communities]
    # 使用获得的 IDs 从 Community 表中检索详绑信息
    communities = models.Community.objects.filter(cid__in=community_ids)
    # 准备返回的数据，例如：
    communitys = [{
        "community_name": community.cname,
        "community_style": community.music_type,
        "community_picture_url": community.profile_picture_url,
        "community_description": community.introduction,
        "community_follow_time": time,
        "community_recent_interaction_star_rating": 4,
    } for community,time in zip(communities,followe_time)]
    return JsonResponse(Result.success(
        {
            'all_community': communitys
        }
    ))
