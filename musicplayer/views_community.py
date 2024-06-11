import uuid

from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from musicplayer.models_sqlview import SongView
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
def userFollowCommunity(request):
    if request.method != 'POST':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, POST only'.format(request.method)
        ))
    data = request.POST
    encode_jwt = data.get('encode_jwt')
    community_id = data.get('community_id')

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

    community = models.Community.objects.get(cid=community_id)
    if community is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='invalid community id',
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

    return JsonResponse(Result.success(
        [
            {
                "community_name": community.cname,
                "community_style": community.music_type,
                "community_picture_url": community.profile_picture_url,
                "community_description": community.introduction,
                "community_follow_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                "community_recent_interaction_star_rating": 4,
            } for community, time in zip(communities, followe_time)
        ]
    ))


@csrf_exempt
def addSongToCommunity(request):
    if request.method != 'POST':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, POST only'.format(request.method)
        ))

    community_id = request.POST.get('community_id')
    song_id = request.POST.get('song_id')

    record = models.SongAndCommunity.objects.filter(
        community_id=community_id,
        song_id=song_id,
    ).first()

    if record is not None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='song already in community'
        ))

    models.SongAndCommunity.objects.create(
        community_id=community_id,
        song_id=song_id,
    )

    return JsonResponse(Result.success())


# 关键字搜索社群
def searchCommunity(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))
    search_content = request.GET.get('search_content')
    if search_content is None or search_content == '':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='search content cannot be empty'
        ))

    filter_conditions = Q()
    filter_conditions |= Q(cname__icontains=search_content)
    filter_conditions |= Q(music_type__icontains=search_content)
    filter_conditions |= Q(introduction__icontains=search_content)
    community_set = models.Community.objects.filter(filter_conditions).distinct().all()

    return JsonResponse(Result.success(
        [
            {
                "cid": community.cid,
                "cname": community.cname,
                "music_style": community.music_type,
                "profile_picture_url": community.profile_picture_url,
                "introduction": community.introduction,
                "recent_interaction_star_rating": 4
            }
            for community in community_set
        ]
    ))


# 展示top5社群（全局）
def showTop5Community(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    community_follow_counts = models.UserFollowCommunity.objects.values('community') \
        .annotate(followers_count=Count('ordinaryUser', distinct=True)).order_by('-followers_count')

    follows = [item['followers_count'] for item in community_follow_counts]
    communities_ids = [item['community'] for item in community_follow_counts]
    communities = models.Community.objects.filter(cid__in=communities_ids)
    return JsonResponse(Result.success(
        [
            {
                "community": {
                    "cid": community.cid,
                    "cname": community.cname,
                    "profile_picture_url": community.profile_picture_url,
                    "music_type": community.music_type,
                    "introduction": community.introduction,
                    "create_time": community.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "update_time": community.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                },
                "community_followers": num,
            }
            for community, num in zip(communities, follows)
        ]
    ))


# 展示用户前5评论最多的社群
def showUserTop5Community(request):
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

    community_follow_counts = models.UserFollowCommunity.objects.filter(
        ordinaryUser=ordinary_user
    ).values('community').annotate(
        followers_count=Count('ordinaryUser', distinct=True)
    ).order_by('-followers_count')

    follows = [item['followers_count'] for item in community_follow_counts]
    communities_ids = [item['community'] for item in community_follow_counts]
    communities = models.Community.objects.filter(cid__in=communities_ids)
    return JsonResponse(Result.success(
        [
            {
                "community_name": community.cname,
                "profile_picture_url": community.profile_picture_url,
                "community_follows": num,
            }
            for community, num in zip(communities, follows)
        ]
    ))


# yulo create something after here
def getDailyBgmOfCommunity(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    community_id = request.GET.get('community_id')

    song_list = [
        song_id for song_id in models.SongAndCommunity.objects.filter(
            community_id=community_id
        ).values_list('song_id', flat=True).all()
    ]

    if len(song_list) == 0:

        song_list = [
            song_id for song_id in models.Song.objects.values_list('sid').all()
        ]

        if len(song_list) == 0:
            return JsonResponse(Result.failure(
                code=Result.HTTP_STATUS_INTERNAL_SERVER_ERROR,
                message='empty song list'
            ))

    seed_index = utils.get_date_seed() % len(song_list)

    dst_song_id = song_list[seed_index]

    song_view = models_sqlview.SongView.objects.filter(
        sid=dst_song_id
    ).first()

    return JsonResponse(Result.success(
        {
            'song_sid': song_view.sid,
            'song_sname': song_view.sname,
            'song_play_count': song_view.play_count,

            'album_aid': song_view.aid,
            'album_aname': song_view.aname,
            'album_cover_url': song_view.cover_url,

            'producer_pid': song_view.pid,
            'producer_username': song_view.username,
        }

    ))


def queryUserInCommunity(request):
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

    user_community_follow_count = models.UserFollowCommunity.objects.filter(
        ordinaryUser=ordinary_user
    ).count()

    return JsonResponse(Result.success(
        {
            'user_id': ordinary_user.uid,
            'user_profile_picture_url': ordinary_user.profile_picture_url,
            'community_amount': user_community_follow_count,
            'message_amount': 0,
            'personal_post_amount': 0
        }
    ))


@csrf_exempt
def postBlog(request):
    if request.method != 'POST':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, POST only'.format(request.method)
        ))

    encode_jwt = request.POST.get('encode_jwt')
    community_id = request.POST.get('community_id')
    text_content = request.POST.get('text_content')

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

    user_follow_community = models.UserFollowCommunity.objects.filter(
        ordinaryUser=ordinary_user,
        community_id=community_id,
    ).first()

    if user_follow_community is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='user has not followed the community'
        ))

    models.Blog.objects.create(
        ordinaryUser=ordinary_user,
        community=user_follow_community.community,

        content=text_content,
    )

    return JsonResponse(Result.success())


@csrf_exempt
def likeBlog(request):
    if request.method != 'POST':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, POST only'.format(request.method)
        ))

    encode_jwt = request.POST.get('encode_jwt')
    blog_bid = request.POST.get('blog_bid')

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

    dst_blog = models.Blog.objects.filter(bid=blog_bid).first()

    if dst_blog is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='no such blog'
        ))

    dst_blog.likes += 1
    dst_blog.save()

    models.Message.objects.create(
        sender=ordinary_user,
        receiver=dst_blog.ordinaryUser,
        message='{} liked your blog'.format(ordinary_user.username)
    )

    return JsonResponse(Result.success())


def queryBlogOfCommunity(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    community_id = request.GET.get('community_id')

    blog_set = models.Blog.objects.filter(community_id=community_id).all()

    return JsonResponse(Result.success(
        [
            {
                'blog': {
                    'bid': blog.bid,
                    'content': blog.content,
                    'likes': blog.likes,
                    'create_time': blog.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'update_time': blog.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                },
                'user': {
                    'uid': blog.ordinaryUser.uid,
                    'username': blog.ordinaryUser.username,
                    'profile_picture_url': blog.ordinaryUser.profile_picture_url,
                }
            }
            for blog in blog_set
        ]
    ))


def getBlogComment(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    blog_id = request.GET.get('blog_id')
    order = request.GET.get('order')

    if order == 'hot':
        order_to_orm = '-likes'
    else:
        order_to_orm = '-release_time'

    blog_comment_set = models.BlogComment.objects.filter(
        blog_id=blog_id
    ).order_by(order_to_orm)

    return JsonResponse(Result.success(
        [
            {
                'blog_comment': {
                    'comment': blog_comment.comment,
                    'blog_likes': blog_comment.likes,
                    'release_time': blog_comment.release_time.strftime("%Y-%m-%d %H:%M:%S")
                },
                'user': {
                    'uid': blog_comment.ordinaryUser.uid,
                    'username': blog_comment.ordinaryUser.username,
                    'profile_picture_url': blog_comment.ordinaryUser.profile_picture_url
                }
            }
            for blog_comment in blog_comment_set
        ]
    ))


def getSongInCommunity(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    community_id = request.GET.get('community_id')

    song_id_list = models.SongAndCommunity.objects.filter(
        community_id=community_id
    ).values_list('song_id', flat=True).all()

    song_view_list = models_sqlview.SongView.objects.filter(
        sid__in=song_id_list
    ).order_by('-play_count').all()

    return JsonResponse(Result.success(
        [
            {
                'song_sid': song_view.sid,
                'song_sname': song_view.sname,
                'song_play_count': song_view.play_count,

                'album_aid': song_view.aid,
                'album_aname': song_view.aname,
                'album_cover_url': song_view.cover_url,

                'producer_pid': song_view.pid,
                'producer_username': song_view.username,
            }

            for song_view in song_view_list
        ]
    ))


# yulo create end


# ldy create after here

# 发布评论
@csrf_exempt
def postBlogComment(request):
    if request.method != 'POST':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, POST only'.format(request.method)
        ))

    encode_jwt = request.POST.get('encode_jwt')
    comment_content = request.POST.get('comment_content')
    blog_id = request.POST.get('blog_id')

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

    if comment_content is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='comment content cannot be empty'
        ))

    dst_blog = models.Blog.objects.filter(bid=blog_id).first()

    if dst_blog is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='invalid blog id',
        ))

    models.BlogComment.objects.create(blog=dst_blog, comment=comment_content, ordinaryUser=ordinary_user)

    return JsonResponse(Result.success())


# 查询用户所有帖子
def getUserAllBriefBlog(request):
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

    blog_set = models.Blog.objects.filter(ordinaryUser=ordinary_user).all()

    return JsonResponse(Result.success(
        [
            {
                "community": blog.community.cname,
                "post_date": blog.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                "post_brief_content": {
                    "content": blog.content,
                    "likes": blog.likes,
                }
            }
            for blog in blog_set
        ]
    ))


# 用户的所有帖子与所有评论
def getUserAllBlog(request):
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
    blogs_set = models.Blog.objects.filter(ordinaryUser=ordinary_user).all().order_by('-create_time')
    blogs_info = []
    for blog in blogs_set:
        comment_info = []
        comments = models.BlogComment.objects.filter(blog=blog).all().order_by('-release_time')
        for comment in comments:
            comment_info.append({"likes": comment.likes, "comment": comment.comment,
                                 "comment_username": comment.ordinaryUser.username,
                                 "comment_time": comment.release_time})
        blogs_info.append(comment_info)

    return JsonResponse(Result.success(
        [
            {
                'post': {
                    "community": Blog.community.cname,
                    "post_date": Blog.create_time,
                    "content": {
                        "content": Blog.content,
                        "likes": Blog.likes,
                    }
                },
                'comment': [
                    {
                        'comment': comment['comment'],
                        'likes': comment['likes'],
                        'comment_time': comment['comment_time'],
                        'comment_username': comment['comment_username'],
                    }
                    for comment in blogs_info[index]
                ]

            }
            for index, Blog in enumerate(blogs_set)
        ]

    ))

# ldy end
