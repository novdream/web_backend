import uuid

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from utils.modelOperation import decodeJwtToken
from utils.result import Result
from utils import utils
from musicplayer import models
from utils.oss2Utils import OSS2Utils


# Create your views here.

@csrf_exempt
def applyProducer(request):
    if request.method != 'POST':
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_METHOD_NOT_ALLOWED,
            message='Method {} not allowed, POST only'.format(request.method)
        ))

    produce_ptype = request.POST.get('ptype')
    produce_title = request.POST.get('title')
    produce_authentication = request.POST.get('authentication')

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

    if ordinary_user.producer is not None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_CONFLICT,
            message='producer has been register'
        ))

    new_producer = models.Producer.objects.create(
        ptype=produce_ptype,
        title=produce_title,
        authentication=produce_authentication,
    )

    ordinary_user.producer = new_producer

    ordinary_user.save()

    return JsonResponse(Result.success())


@csrf_exempt
def createSong(request):
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

    # 查看用户是否有创作者权限
    producer = ordinary_user.producer

    if producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='producer authority required'
        ))

    album_id = request.POST.get('album_id')

    # 检查album_id 是否有效
    if not models.Album.objects.filter(aid=album_id).exists():
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='invalid album id'
        ))

    song_name = request.POST.get('song_name')
    song_type = request.POST.get('song_type')
    song_version = request.POST.get('song_version')

    song_language = request.POST.get('song_language')
    music_style = request.POST.get('music_style')

    song_metadata = request.POST.get('song_metadata')
    song_introduction = request.POST.get('song_introduction')

    new_song = models.Song.objects.create(
        producer=producer,
        album_id=album_id,

        sname=song_name,
        stype=song_type,
        sversion=song_version,

        language_type=song_language,
        music_style=music_style,
        metadata=song_metadata,
        introduction=song_introduction,
    )

    return JsonResponse(Result.success(new_song.sid))


@csrf_exempt
def modifySong(request):
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

    # 查看用户是否有创作者权限
    producer = ordinary_user.producer

    if producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='producer authority required'
        ))

    # 检查歌曲的作者是否为当前创作者
    song_id = request.POST.get('song_id')

    song_to_modify = models.Song.objects.filter(
        sid=song_id,
        producer=producer,
    ).first()

    if song_to_modify is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='no song founded'
        ))

    song_name = request.POST.get('song_name')
    song_type = request.POST.get('song_type')
    song_version = request.POST.get('song_version')

    song_language = request.POST.get('song_language')
    music_style = request.POST.get('music_style')

    song_metadata = request.POST.get('song_metadata')
    song_introduction = request.POST.get('song_introduction')

    if song_name is not None and song_name != '':
        song_to_modify.sname = song_name

    if song_type is not None and song_type != '':
        song_to_modify.stype = song_type

    if song_version is not None and song_version != '':
        song_to_modify.sversion = song_version

    if song_language is not None and song_language != '':
        song_to_modify.language_type = song_language

    if music_style is not None and music_style != '':
        song_to_modify.music_style = music_style

    if song_metadata is not None and song_metadata != '':
        song_to_modify.metadata = song_metadata

    if song_introduction is not None and song_introduction != '':
        song_to_modify.introduction = song_introduction

    song_to_modify.save()

    return JsonResponse(Result.success())


@csrf_exempt
def uploadSongAudio(request):
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

    # 查看用户是否有创作者权限
    producer = ordinary_user.producer

    if producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='producer authority required'
        ))

    # 检查歌曲的作者是否为当前创作者
    song_id = request.POST.get('song_id')

    song_to_modify = models.Song.objects.filter(
        sid=song_id,
        producer=producer,
    ).first()

    if song_to_modify is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='no song founded'
        ))

    # 获取音频文件
    audio_file = request.FILES.get('audio_file')

    if audio_file is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_BAD_REQUEST,
            message='no audio file founded'
        ))

    audio_file_extension = utils.checkFileExtension(
        filename=audio_file.name,
        allowed_extensions=['.wav', '.mp3', '.ogg']
    )

    # 如果扩展名检验失败
    if audio_file_extension is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='invalid song file extension',
        ))

    # 歌曲音頻文件的uuid
    oss_song_filename = uuid.uuid4().hex + audio_file_extension

    # 调用云服务上传音頻文件
    upload_audio_url = OSS2Utils.upload(
        request_file=audio_file,
        oss_filename=oss_song_filename,
        oss_folder=['song', 'audio']
    )

    if upload_audio_url is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_INTERNAL_SERVER_ERROR,
            message='upload file failed'
        ))

    song_to_modify.audio_url = upload_audio_url
    song_to_modify.save()

    return JsonResponse(Result.success())


@csrf_exempt
def upLoadSongLyrics(request):
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

    # 查看用户是否有创作者权限
    producer = ordinary_user.producer

    if producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='producer authority required'
        ))

    # 检查歌曲的作者是否为当前创作者
    song_id = request.POST.get('song_id')

    song_to_modify = models.Song.objects.filter(
        sid=song_id,
        producer=producer,
    ).first()

    if song_to_modify is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='no song founded'
        ))

    # 获取歌词文件

    lyrics_file = request.POST.get('lyrics_file')

    if lyrics_file is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_BAD_REQUEST,
            message='no lyrics file founded'
        ))

    # 检查文件后缀名
    lyrics_file_extension = utils.checkFileExtension(
        filename=lyrics_file.name,
        allowed_extensions=['.lrc']
    )

    if lyrics_file_extension is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='invalid lyrics file extension'
        ))

    # 生成歌词文件的uuid
    oss_lyrics_filename = uuid.uuid4().hex + lyrics_file_extension

    # 调用云服务
    upload_lyrics_url = OSS2Utils.upload(
        request_file=lyrics_file,
        oss_filename=oss_lyrics_filename,
        oss_folder=['song', 'lyrics']
    )

    if upload_lyrics_url is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_INTERNAL_SERVER_ERROR,
            message='upload file failed',
        ))

    song_to_modify.lyrics_utl = upload_lyrics_url
    song_to_modify.save()

    return JsonResponse(Result.success())


@csrf_exempt
def createAlbum(request):
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

    # 查看用户是否有创作者权限
    producer = ordinary_user.producer

    if producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='producer authority required'
        ))

    album_name = request.POST.get('album_name')
    album_type = request.POST.get('album_type')
    album_release_date_str = request.POST.get('album_release_date')

    album_introduction = request.POST.get('album_introduction')

    album_release_date = None
    if album_release_date_str is not None:
        album_release_date = utils.strToDate(album_release_date_str)
        if album_release_date is None:
            return JsonResponse(Result.failure(
                code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
                message='invalid date format'
            ))

    new_album = models.Album.objects.create(
        producer=producer,
        aname=album_name,
        atype=album_type,
        release_date=album_release_date,
        introduction=album_introduction,
    )

    return JsonResponse(Result.success(new_album.aid))


@csrf_exempt
def modifyAlbum(request):
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

    # 查看用户是否有创作者权限
    producer = ordinary_user.producer

    if producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='producer authority required'
        ))

    # 检查歌曲的作者是否为当前创作者
    album_id = request.POST.get('album_id')

    album_to_modify = models.Album.objects.filter(
        aid=album_id,
        producer=producer,
    ).first()

    if album_to_modify is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='no song founded'
        ))

    album_name = request.POST.get('album_name')
    album_type = request.POST.get('album_type')

    album_release_date_str = request.POST.get('album_release_date')
    album_introduction = request.POST.get('album_introduction')

    if album_name is not None and album_name != '':
        album_to_modify.aname = album_name

    if album_type is not None and album_type != '':
        album_to_modify.atype = album_type

    if album_release_date_str is not None and album_release_date_str != '':

        album_release_date = utils.strToDate(album_release_date_str)

        # 日期格式转换错误
        if album_release_date is None:
            return JsonResponse(Result.failure(
                code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
                message='invalid date format'
            ))

        album_to_modify.release_date = album_release_date

    if album_introduction is not None and album_introduction != '':
        album_to_modify.introduction = album_introduction

    album_to_modify.save()

    return JsonResponse(Result.success())


@csrf_exempt
def uploadAlbumCover(request):
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

    # 查看用户是否有创作者权限
    producer = ordinary_user.producer

    if producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='producer authority required'
        ))

    # 检查歌曲的作者是否为当前创作者
    album_id = request.POST.get('album_id')

    album_to_modify = models.Album.objects.filter(
        aid=album_id,
        producer=producer,
    ).first()

    if album_to_modify is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='no album founded'
        ))

    # 获取专辑封面
    album_cover_file = request.FILES.get('album_cover')

    if album_cover_file is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_BAD_REQUEST,
            message='no album cover file founded'
        ))

    album_cover_extension = utils.checkFileExtension(
        filename=album_cover_file.name,
        allowed_extensions=['.jpg', '.jpeg', '.png']
    )

    # 如果扩展名检验失败
    if album_cover_extension is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='invalid file extension',
        ))

    # 专辑封面文件的uuid
    oss_filename = uuid.uuid4().hex + album_cover_extension

    # 调用云服务上传封面文件
    upload_cover_url = OSS2Utils.upload(
        request_file=album_cover_file,
        oss_filename=oss_filename,
        oss_folder=['album', 'cover']
    )

    if upload_cover_url is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_INTERNAL_SERVER_ERROR,
            message='upload file failed'
        ))

    album_to_modify.cover_url = upload_cover_url

    album_to_modify.save()

    return JsonResponse(Result.success())


def querySongOfProducer(request):
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

    # 查看用户是否有创作者权限
    producer = ordinary_user.producer

    if producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='producer authority required'
        ))

    song_queryset_list = [
        {
            'sid': song_iterator.sid,
            'producer_pid': song_iterator.producer_id,
            'album_aid': song_iterator.album_id,

            'audio_url': song_iterator.audio_url,
            'lyrics_url': song_iterator.lyrics_url,

            'sname': song_iterator.sname,
            'stype': song_iterator.stype,
            'sversion': song_iterator.sversion,

            'language_type': song_iterator.language_type,
            'music_style': song_iterator.music_style,
            'metadata': song_iterator.metadata,
            'introduction': song_iterator.introduction,

            'create_time': song_iterator.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': song_iterator.update_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for song_iterator in models.Song.objects.filter(producer=producer).all()
    ]

    return JsonResponse(Result.success(song_queryset_list))


def queryAlbumOfProducer(request):
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

    # 查看用户是否有创作者权限
    producer = ordinary_user.producer

    if producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='producer authority required'
        ))

    album_query_list = [
        {
            'aid': album_iterator.aid,
            'producer_pid': album_iterator.producer_id,

            'aname': album_iterator.aname,
            'atype': album_iterator.atype,
            'release_date': album_iterator.release_date,

            'introduction': album_iterator.introduction,
            'cover_url': album_iterator.cover_url,

            'create_time': album_iterator.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': album_iterator.update_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for album_iterator in models.Album.objects.filter(producer=producer).all()
    ]

    return JsonResponse(Result.success(album_query_list))


def queryProducer(request):
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

    # 查看用户是否有创作者权限
    producer = ordinary_user.producer

    if producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='producer authority required'
        ))

    producer_view = {
        'username': ordinary_user.username,

        'ptype': producer.ptype,
        'title': producer.title,
        'authentication': producer.authentication,

        'create_time': producer.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        'update_time': producer.update_time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    return JsonResponse(Result.success(producer_view))


def queryFansOfProducer(request):
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

    # 查看用户是否有创作者权限
    producer = ordinary_user.producer

    if producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='producer authority required'
        ))

    follow_querylist = models.UserFollowProducer.objects.filter(
        producer=producer,
    ).all()

    return JsonResponse(Result.success(
        [
            {
                'user': {
                    'uid': follow_iterator.ordinaryUser.uid,
                    'username': follow_iterator.ordinaryUser.username,
                    'profile_photo_url': follow_iterator.ordinaryUser.profile_picture_url,
                },
                'follow_time': follow_iterator.follow_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            for follow_iterator in follow_querylist
        ]
    ))


@csrf_exempt
def createSongCollaboration(request):
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

    # 查看用户是否有创作者权限
    song_producer = ordinary_user.producer

    if song_producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='producer authority required'
        ))

    song_sid = request.POST.get('song_sid')

    dst_song = models.Song.objects.filter(
        sid=song_sid,
        producer=song_producer
    ).first()

    if dst_song is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='no song founded'
        ))

    joint_producer_pid = request.POST.get('producer_pid')

    joint_producer = models.Producer.objects.filter(
        pid=joint_producer_pid,
    ).exclude(
        pid=song_producer.pid,
    ).first()

    if joint_producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='no joint producer founded'
        ))

    joint_role = request.POST.get('role')

    if models.SongAndProducer.objects.filter(
        song=dst_song,
        producer=joint_producer,
    ).count() != 0:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_CONFLICT,
            message='song-collaboration already exists'
        ))

    models.SongAndProducer.objects.create(
        song=dst_song,
        producer=joint_producer,
        role=joint_role,
        status='p',
    )

    # FUTURE TODO: 在此处通知联合投稿的创作者确认或拒绝联合投稿,把消息存入数据库中?

    return JsonResponse(Result.success())


@csrf_exempt
def handleSongCollaboration(request):
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

    # 查看用户是否有创作者权限
    song_producer = ordinary_user.producer

    if song_producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='producer authority required'
        ))

    song_sid = request.POST.get('song_sid')

    dst_record = models.SongAndProducer.objects.filter(
        song_id=song_sid,
        producer=song_producer,
        status='p',
    ).first()

    if dst_record is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_NOT_ACCEPTABLE,
            message='no song-collaboration record found'
        ))

    confirm = request.POST.get('confirm')

    if confirm == 'y':
        dst_record.status = 'c'
    else:
        dst_record.status = 'r'

    dst_record.save()

    return JsonResponse(Result.success())


def querySongCollaboration(request):

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

    # 查看用户是否有创作者权限
    producer = ordinary_user.producer

    if producer is None:
        return JsonResponse(Result.failure(
            code=Result.HTTP_STATUS_UNAUTHORIZED,
            message='producer authority required'
        ))

    collaboration_status = request.GET.get('collaboration_status')

    filter_condition = Q()

    if collaboration_status in ('p', 'c', 'r'):
        filter_condition &= Q(status=collaboration_status)

    filter_condition &= Q(producer=producer)

    collaborations_queryset = models.SongAndProducer.objects.filter(
        filter_condition
    ).extra(
        select={
            'producer_name': 'producer_view.username',
            'producer_profile_picture_url': 'producer_view.profile_picture_url',
        },

        tables=['producer_view'],
        where=['musicplayer_songandproducer.producer_id = producer_view.pid']
    ).all()

    return JsonResponse(Result.success(
        [
            {
                'song': {
                    'sid': collaboration_iterator.song.sid,
                    'sname': collaboration_iterator.song.sname,
                    'sversion': collaboration_iterator.song.sversion,
                },

                'producer': {
                    'pid': collaboration_iterator.producer.pid,
                    'name': collaboration_iterator.producer_name,
                    'profile_picture_url': collaboration_iterator.producer_profile_picture_url
                },

                'status': collaboration_iterator.status,
                'role': collaboration_iterator.role,
                'create_time': collaboration_iterator.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'update_time': collaboration_iterator.update_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for collaboration_iterator in collaborations_queryset
        ]
    ))




