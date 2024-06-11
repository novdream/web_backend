import uuid

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from utils.modelOperation import decodeJwtToken
from utils.oss2Utils import OSS2Utils
from utils.result import Result
from utils import utils
from musicplayer import models, models_sqlview


def queryProducerById(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    producer_pid = request.GET.get('producer_pid')

    producer_view = models_sqlview.ProducerView.objects.filter(pid=producer_pid).first()

    if producer_view is None:
        return JsonResponse(Result.success(None))

    return JsonResponse(Result.success(
        {
            'name': producer_view.username,
            'profile_picture_url': producer_view.profile_picture_url,
            'gender': producer_view.gender,
            'introduction': producer_view.introduction,

            'ptype': producer_view.ptype,
            'title': producer_view.title,
            'authentication': producer_view.authentication
        }
    ))


def querySongById(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    song_sid = request.GET.get('song_sid')

    song_info = models.Song.objects.filter(sid=song_sid).extra(
        select={
            'producer_name': 'producer_view.username',
            'producer_profile_picture_url': 'producer_view.profile_picture_url',
        },
        tables=['producer_view'],
        where=['musicplayer_song.producer_id = producer_view.pid']
    ).first()

    if song_info is None:
        return JsonResponse(Result.success(None))

    return JsonResponse(Result.success(
        {
            'producer': {
                'pid': song_info.producer_id,
                'name': song_info.producer_name,
                'profile_picture_url': song_info.producer_profile_picture_url,
            },

            'album': {
                'aid': song_info.album.aid,
                'aname': song_info.album.aname,
                'cover_url': song_info.album.cover_url
            },

            'audio_url': song_info.audio_url,
            'lyrics_url': song_info.lyrics_url,

            'sname': song_info.sname,
            'stype': song_info.stype,
            'sversion': song_info.sversion,

            'language_type': song_info.language_type,
            'music_style': song_info.music_style,
            'metadata': song_info.metadata,
            'introduction': song_info.introduction,
        }
    ))


@csrf_exempt
def createSongList(request):
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

    songlist_title = request.POST.get('songlist_title')
    cover_picture = request.FILES.get('cover_picture')

    if cover_picture is None:
        new_songlist = models.SongList.objects.create(
            ordinaryUser=ordinary_user,
            title=songlist_title,
        )
        return JsonResponse(Result.success(new_songlist.slid))

    cover_picture_extension = utils.checkFileExtension(
        filename=cover_picture.name,
        allowed_extensions=['.jpg', '.png', '.jpeg']
    )

    # 扩展名检验失败
    if cover_picture_extension is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='invalid file extension'
        ))

    # 生成uuid
    oss_filename = uuid.uuid4().hex + cover_picture_extension

    # 调用云服务上传
    upload_cover_url = OSS2Utils.upload(
        request_file=cover_picture,
        oss_filename=oss_filename,
        oss_folder=['songlist', 'cover']
    )

    if upload_cover_url is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_INTERNAL_SERVER_ERROR,
            message='upload file failed',
        ))

    new_songlist = models.SongList.objects.create(
        ordinaryUser=ordinary_user,
        title=songlist_title,
        cover_picture_url=upload_cover_url,
    )

    return JsonResponse(Result.success(new_songlist.slid))


@csrf_exempt
def modifySongList(request):
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

    songlist_slid = request.POST.get('songlist_slid')
    songlist_title = request.POST.get('songlist_title')

    dst_songlist = models.SongList.objects.filter(
        ordinaryUser=ordinary_user,
        slid=songlist_slid,
    ).first()

    if dst_songlist is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='song list not found',
        ))

    if songlist_title is not None:
        dst_songlist.title = songlist_title

    songlist_cover = request.FILES.get('songlist_cover')

    if songlist_cover is None:
        dst_songlist.save()
        return JsonResponse(Result.success())

    songlist_cover_extension = utils.checkFileExtension(
        filename=songlist_cover.name,
        allowed_extensions=['.jpg', '.jpeg', '.png']
    )

    # 扩展名检验失败
    if songlist_cover_extension is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='invalid file extension'
        ))

    # 生成uuid
    oss_filename = uuid.uuid4().hex + songlist_cover_extension

    # 调用云服务上传
    upload_cover_url = OSS2Utils.upload(
        request_file=songlist_cover,
        oss_filename=oss_filename,
        oss_folder=['songlist', 'cover']
    )

    if upload_cover_url is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_INTERNAL_SERVER_ERROR,
            message='upload file failed',
        ))

    dst_songlist.cover_picture_url = upload_cover_url

    dst_songlist.save()

    return JsonResponse(Result.success())


def querySongList(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    songlist_sid = request.GET.get('songlist_slid')

    dst_songlist = models.SongList.objects.filter(
        slid=songlist_sid,
    ).first()

    if dst_songlist is None:
        return JsonResponse(Result.success(None))

    # 从关联表中查询所有的song

    dst_song_queryset = models.SongAndSongList.objects.filter(
        songList=dst_songlist
    ).all()

    # 从歌曲简要信息列表中查询song

    song_info_list = models_sqlview.SongView.objects.filter(
        sid__in=[songlist_iterator.song_id for songlist_iterator in dst_song_queryset]
    ).all()

    return JsonResponse(Result.success(
        {
            'title': dst_songlist.title,
            'cover_picture_url': dst_songlist.cover_picture_url,
            'create_time': dst_songlist.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': dst_songlist.update_time.strftime('%Y-%m-%d %H:%M:%S'),

            'user': {
                'uid': dst_songlist.ordinaryUser.uid,
                'username': dst_songlist.ordinaryUser.username,
                'profile_picture_url': dst_songlist.ordinaryUser.profile_picture_url,
            },

            'song_list': [
                {
                    'sid': song_iterator.sid,
                    'sname': song_iterator.sname,
                    'play_back': song_iterator.play_back,

                    'album_aid': song_iterator.aid,
                    'album_aname': song_iterator.aname,
                    'album_cover_url': song_iterator.cover_url,

                    'producer_pid': song_iterator.pid,
                    'producer_username': song_iterator.username,
                }
                for song_iterator in song_info_list
            ],
        }
    ))


@csrf_exempt
def addSongToSongList(request):
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

    songlist_slid = request.POST.get('songlist_slid')
    song_sid = request.POST.get('song_sid')

    dst_songlist = models.SongList.objects.filter(
        slid=songlist_slid,
        ordinaryUser=ordinary_user,
    ).first()

    if dst_songlist is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='song list not found',
        ))

    dst_song = models.Song.objects.filter(sid=song_sid).first()

    if dst_song is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='song not found',
        ))

    if models.SongAndSongList.objects.filter(
            songList=dst_songlist,
            song=dst_song,
    ).count() != 0:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_CONFLICT,
            message='record already exists'
        ))

    models.SongAndSongList.objects.create(
        songList=dst_songlist,
        song=dst_song,
    )

    return JsonResponse(Result.success())


@csrf_exempt
def dropSongFromSongList(request):
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

    songlist_slid = request.POST.get('songlist_slid')
    song_sid = request.POST.get('song_sid')

    dst_songlist = models.SongList.objects.filter(
        slid=songlist_slid,
        ordinaryUser=ordinary_user,
    ).first()

    if dst_songlist is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='song list not found',
        ))

    dst_song = models.Song.objects.filter(sid=song_sid).first()

    if dst_song is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='song not found',
        ))

    if models.SongAndSongList.objects.filter(
            songList=dst_songlist,
            song=dst_song,
    ).count() == 0:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='no such record'
        ))

    models.SongAndSongList.objects.filter(
        songList=dst_songlist,
        song=dst_song,
    ).delete()

    return JsonResponse(Result.success())


def querySongByAlbum(request):

    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    album_aid = request.GET.get('album_aid')

    dst_album = models.Album.objects.filter(
        aid=album_aid
    ).first()

    if dst_album is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_FOUND,
            message='album not found'
        ))

    dst_songview_list = models_sqlview.SongView.objects.filter(
        aid=dst_album.aid
    ).all()

    return JsonResponse(Result.success(
        [
            {
                'sid': song_iterator.sid,
                'sname': song_iterator.sname,
                'play_back': song_iterator.play_back,

                'album_aid': song_iterator.aid,
                'album_aname': song_iterator.aname,
                'album_cover_url': song_iterator.cover_url,

                'producer_pid': song_iterator.pid,
                'producer_username': song_iterator.username,
            }
            for song_iterator in dst_songview_list
        ],
    ))


def querySongByProducer(request):

    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    producer_pid = request.GET.get('producer_pid')

    dst_producer = models.Producer.objects.filter(
        pid=producer_pid
    ).first()

    if dst_producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_FOUND,
            message='producer not found'
        ))

    # 由该创作者投稿的歌曲
    directupload_songview_list = models_sqlview.SongView.objects.filter(
        pid=dst_producer.pid
    ).all()

    # 该创作者与其他创作者联合投稿的歌曲
    collaborate_songsid_list = models.SongAndProducer.objects.filter(
        producer=dst_producer,
        status='c',
    ).values_list('song_id', flat=True).all()

    collaborate_songview_list = models_sqlview.SongView.objects.filter(
        sid__in=collaborate_songsid_list
    ).all()

    return JsonResponse(Result.success(
        {
            "producer_upload": [
                {
                    'sid': song_iterator.sid,
                    'sname': song_iterator.sname,
                    'play_back': song_iterator.play_back,

                    'album_aid': song_iterator.aid,
                    'album_aname': song_iterator.aname,
                    'album_cover_url': song_iterator.cover_url,

                    'producer_pid': song_iterator.pid,
                    'producer_username': song_iterator.username,
                }
                for song_iterator in directupload_songview_list
            ],
            "collaborate": [
                {
                    'sid': song_iterator.sid,
                    'sname': song_iterator.sname,
                    'play_back': song_iterator.play_back,

                    'album_aid': song_iterator.aid,
                    'album_aname': song_iterator.aname,
                    'album_cover_url': song_iterator.cover_url,

                    'producer_pid': song_iterator.pid,
                    'producer_username': song_iterator.username,
                }
                for song_iterator in collaborate_songview_list
            ]
        }
    ))


@csrf_exempt
def createSongComment(request):
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

    song_id = request.POST.get('song_sid')

    dst_song = models.Song.objects.filter(sid=song_id).first()

    if dst_song is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='song not found'
        ))

    comment_content = request.POST.get('content')

    new_song_comment = models.SongComment.objects.create(
        song=dst_song,
        ordinaryUser=ordinary_user,
        comment=comment_content,
    )

    return JsonResponse(Result.success(new_song_comment.scid))


@csrf_exempt
def dropSongComment(request):
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

    song_comment_scid = request.POST.get('song_comment_scid')

    dst_song_comment = models.SongComment.objects.filter(
        scid=song_comment_scid,
        ordinaryUser=ordinary_user,
    )

    if dst_song_comment is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='song comment not found'
        ))

    dst_song_comment.delete()

    return JsonResponse(Result.success())


def querySongComment(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    song_sid = request.GET.get('song_sid')

    dst_song = models.Song.objects.filter(sid=song_sid).first()

    if dst_song is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='no such song'
        ))

    song_comment_queryset = models.SongComment.objects.filter(song=dst_song).all()

    return_data = [
        {
            'user': {
                'uid': song_comment_iterator.ordinaryUser.uid,
                'username': song_comment_iterator.ordinaryUser.username,
                'profile_picture_url': song_comment_iterator.ordinaryUser.profile_picture_url,
            },

            'comment': song_comment_iterator.comment,
            'release_time': song_comment_iterator.release_time.strftime('%Y-%m-%d')
        }
        for song_comment_iterator in song_comment_queryset
    ]

    return JsonResponse(Result.success(
        return_data
    ))


def queryProducerByCondition(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    name = request.GET.get('name')
    ptype = request.GET.get('ptype')

    filter_conditions = Q()

    if name:
        filter_conditions &= Q(username__icontains=name)

    if ptype:
        filter_conditions &= Q(ptype=ptype)

    dst_producer = models_sqlview.ProducerView.objects.filter(filter_conditions).all()

    return JsonResponse(Result.success(
        [
            {
                'pid': dst_producer_iterator.pid,
                'name': dst_producer_iterator.username,
                'profile_picture_url': dst_producer_iterator.profile_picture_url,
                'ptype': dst_producer_iterator.ptype,
            }
            for dst_producer_iterator in dst_producer
        ]
    ))


def querySongByCondition(request):
    if request.method != 'GET':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, GET only'.format(request.method)
        ))

    query_condition = request.GET.get('condition')

    filter_conditions = Q()
    filter_conditions |= Q(sname__icontains=query_condition)
    filter_conditions |= Q(aname__icontains=query_condition)
    filter_conditions |= Q(username__icontains=query_condition)

    song_queryset = models_sqlview.SongView.objects.filter(filter_conditions).distinct().all()

    return JsonResponse(Result.success(
        [
            {
                'sid': queryset_iterator.sid,
                'sname': queryset_iterator.sname,

                'aid': queryset_iterator.aid,
                'aname': queryset_iterator.aname,
                'cover_url': queryset_iterator.cover_url,

                'pid': queryset_iterator.pid,
                'producer_name': queryset_iterator.username,
            }
            for queryset_iterator in song_queryset
        ]
    ))


@csrf_exempt
def followProducer(request):
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

    producer_pid = request.POST.get('producer_pid')

    dst_producer = models.Producer.objects.filter(
        pid=producer_pid
    ).first()

    if dst_producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='producer not found'
        ))

    # 用户不能关注自己的producer

    if ordinary_user.producer_id is not None and dst_producer.pid == ordinary_user.producer_id:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='user can not follow himself / herself'
        ))

    models.UserFollowProducer.objects.create(producer=dst_producer, ordinaryUser=ordinary_user)

    return JsonResponse(Result.success())


@csrf_exempt
def cancelFollowProducer(request):
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

    producer_pid = request.POST.get('producer_pid')

    dst_follow_record = models.UserFollowProducer.objects.filter(
        ordinaryUser=ordinary_user,
        producer_id=producer_pid,
    ).first()

    if dst_follow_record is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='user-producer follow record not found'
        ))

    dst_follow_record.delete()

    return JsonResponse(Result.success())


# 播放量+1
@csrf_exempt
def addPlayBack(request):
    if request.method != 'POST':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, POST only'.format(request.method)
        ))
    sid = request.POST.get('song_sid')
    song = models.Song.objects.filter(sid=sid).first()
    if song is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='songId is not found'
        ))
    song.play_back += 1
    song.save()
    return JsonResponse(Result.success())
