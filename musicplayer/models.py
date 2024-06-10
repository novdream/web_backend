import uuid

from django.db import models
from django.utils import timezone

# Create your models here.


"""
    表名：普通用户表
    描述：记录用户的基本信息
    类型：实体
    说明：如果某用户的producer_pid字段不为空，代表用户为创作者
    创作者具体信息储存在producer表中。否则为普通用户
    字段：
    uid - 用户的主键
    producer_pid - 创作者id

    username - 用户名称
    `password` - 用户密码

    phone - 手机号码
    email - 邮箱


    profile_picture_url - 用户头像图片的URL
    sex - 性别， 'm' = 男
    'f' = 女
    birthday - 生日
    region - 用户地区
    introduction - 用户简介

    create_time - 用户注册时间
    update_time - 用户信息最后修改时间
"""


class OrdinaryUser(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    producer = models.ForeignKey('Producer', on_delete=models.SET_NULL, null=True)

    username = models.CharField(max_length=45)
    password = models.CharField(max_length=45)

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=11, null=True)

    profile_picture_url = models.URLField(null=True)
    gender = models.CharField(max_length=1, null=True)
    birthday = models.DateField(null=True)
    region = models.CharField(max_length=45, null=True)
    introduction = models.CharField(max_length=200, null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


"""
    表名：创作者信息表
    描述：记录创作者的基本信息，实现对普通用户的拓展
    类型：实体
    说明：创作者类继承普通用户类，创作者的额外信息在producer表中，对应普通用户producer_pid字段
    字段：
    pid - 创作者主键
    ptype - 创作者类型，枚举值
    例如：歌手、制作人、乐手
    title - 创作者的荣誉称号
    authentication - 认证信息，仿照b站up主的认证信息机制

    create_time - 创作者入驻时间
    update_time - 创作者信息最后修改时间
"""


class Producer(models.Model):
    pid = models.UUIDField(primary_key=True, default=uuid.uuid4)

    ptype = models.CharField(max_length=20, null=True)
    title = models.CharField(max_length=90, null=True)
    authentication = models.CharField(max_length=90, null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


"""
    表名：歌曲信息表
    描述：记录歌曲的信息
    类型：实体
    说明：规定一首歌曲必须属于一个专辑
    字段：
    sid - 歌曲的主键

    producer_pid - 创作者的id
    album_aid - 歌曲所属专辑的id

    sname - 歌曲名称
    stype - 歌曲类型枚举值，例如原创翻唱remix等
    sversion - 歌曲版本，枚举值， 例如
    录音室版
    混音版
    伴奏版
    现场版
    demo版等
    song_url - 歌曲音频资源地址

    language_type - 歌曲语种
    music_style   - 音乐风格
    metadata：     - 歌曲的元信息，以json字符串存储歌曲的作词作曲编曲混音母带等信息
    lyrics - 歌词信息
    introduction - 歌曲介绍

    create_time - 歌曲创建时间
    update_time - 歌曲信息最后修改时间
"""


class Song(models.Model):
    sid = models.UUIDField(primary_key=True, default=uuid.uuid4)

    producer = models.ForeignKey('Producer', on_delete=models.CASCADE)
    album = models.ForeignKey('Album', on_delete=models.CASCADE)

    audio_url = models.URLField(null=True)
    lyrics_url = models.URLField(null=True)

    sname = models.CharField(max_length=45)
    stype = models.CharField(max_length=20, null=True)
    sversion = models.CharField(max_length=20, null=True)

    language_type = models.CharField(max_length=45, null=True)
    music_style = models.CharField(max_length=45, null=True)
    metadata = models.CharField(max_length=200, null=True)
    introduction = models.CharField(max_length=200, null=True)

    play_back = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


"""
    表名：歌曲投稿信息表
    描述：记录歌曲的创作者团队
    类型：关系
    说明：参考b站联合投稿功能，歌曲表的producer字段代表歌曲的上传者，
    即up主歌曲投稿信息表记录其余创作者的贡献角色，例如作词，作曲等

    字段：
    producer_pid		- 创作者id
    song_sid            - 歌曲id
    `role`              - 创作者在歌曲创作中的角色
    
    status              - 联合投稿状态， 如p=发起(post)、c=确认(confirm)、r=拒绝(refuse)
"""


class SongAndProducer(models.Model):
    producer = models.ForeignKey('Producer', on_delete=models.CASCADE)
    song = models.ForeignKey('Song', on_delete=models.CASCADE)

    role = models.CharField(max_length=20, default='')
    status = models.CharField(max_length=1)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['producer', 'song'], ]


"""
    表名：专辑表
    描述：记录专辑的信息
    类型：实体
    说明：每首歌曲都对应一个专辑，专辑可以有多个歌曲
    字段：
    aid                 - 专辑id
    producer_pid        - 专辑创作者的id
    aname               - 专辑名称
    atype               - 专辑类型 ？？？
    aversion            - 专辑版本
    cover_picture_url   - 封面图片地址
    release_date        - 专辑发布时间
    introduction        - 专辑简介

    create_time			- 歌曲创建时间
    update_time	        - 歌曲信息最后修改时间
"""


class Album(models.Model):
    aid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    producer = models.ForeignKey('Producer', on_delete=models.CASCADE)

    aname = models.CharField(max_length=45)
    atype = models.CharField(max_length=20, null=True)
    release_date = models.DateField(null=True)

    introduction = models.CharField(max_length=200, null=True)
    cover_url = models.URLField(null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


"""
    表名：歌单
    描述：记录用户创建歌单的信息 
    类型：实体
    说明：歌单表储存歌单的总体信息，歌单的具体歌曲储存在歌单-歌曲关系表中
    字段：
    slid                - 歌单id
    ordinary_user_uid   - 歌单创建者id

    title               - 歌单标题
    cover_picture_url   - 封面歌单地址

    create_time			- 歌曲创建时间
    update_time	- 歌曲信息最后修改时间
"""


class SongList(models.Model):
    slid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ordinaryUser = models.ForeignKey('OrdinaryUser', on_delete=models.CASCADE)

    title = models.CharField(max_length=45)
    cover_picture_url = models.URLField(null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


"""
    表名：歌曲歌单关系
    描述：存储歌曲和歌单之间的多对多关系
    类型：关系
    说明：仅储存歌曲歌单关系，歌单的具体信息在
    字段：
    song_list_slid      - 歌单id
    song_sid            - 歌曲id
    collect_time        - 用户将歌曲收集进歌单的时间
"""


class SongAndSongList(models.Model):
    songList = models.ForeignKey('SongList', on_delete=models.CASCADE)
    song = models.ForeignKey('Song', on_delete=models.CASCADE)
    collect_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['songList', 'song'], ]


"""
    表名：歌曲评论
    描述：储存歌曲中的评论信息
    类型：实体
    说明：通过歌曲id和用户id表示一条具体的评论
    字段：
    song_sid            - 歌曲id
    ordinary_user_uid   - 用户id
    likes               - 该评论的点赞数
    `comment`           - 评论内容
    release_time        - 评论发布时间
"""


class SongComment(models.Model):
    scid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    song = models.ForeignKey('Song', on_delete=models.CASCADE)
    ordinaryUser = models.ForeignKey('OrdinaryUser', on_delete=models.CASCADE)

    likes = models.IntegerField(default=0)
    comment = models.CharField(max_length=400)
    release_time = models.DateTimeField(auto_now=True)


"""
    表名：用户-创作者关注列表
    描述：记录用户关注的创作者，即创作者的粉丝
    类型：关系
    说明：
    字段：
    producer_pid        - 创作者id
    ordinary_user_uid   - 用户id
    follow_time         - 关注时间
"""


class UserFollowProducer(models.Model):
    producer = models.ForeignKey('Producer', on_delete=models.CASCADE)
    ordinaryUser = models.ForeignKey('OrdinaryUser', on_delete=models.CASCADE)
    follow_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['producer', 'ordinaryUser'], ]


"""
    表名：歌曲社区信息社区表
    描述：歌曲可以属于一个社区，在社区界面可以推荐该歌曲
    类型：关系
    说明：多对对关系
    字段：
    song_sid            - 歌曲id
    community_cid      - 社区id
"""


class SongAndCommunity(models.Model):
    song = models.ForeignKey('Song', on_delete=models.CASCADE)
    community = models.ForeignKey('Community', on_delete=models.CASCADE)

    class Meta:
        unique_together = [['song', 'community'], ]


"""
    表名：社区信息表
    描述：记录一个社群的基本信息
    类型：实体
    说明：多对对关系
    字段：
    cid                 - 社群主键
    cname               - 社群名称
    profile_picture_url - 社群封面图片地址
    music_type          - 社群的音乐主题
    introduction        - 社群简介
"""


class Community(models.Model):
    cid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    cname = models.CharField(max_length=45)
    profile_picture_url = models.URLField(null=True)
    music_type = models.CharField(max_length=60)
    introduction = models.CharField(max_length=200)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


"""
    表名：用户社区信息社区表
    描述：用户与社群之间的关系，包括关注，管理等
    类型：关系
    说明：多对对关系
    字段：
    ordinary_user_uid - 用户主键
    community_cid - 社群主键
    role - 关注者的角色，如吧主 管理员 普通关注等
"""


class UserFollowCommunity(models.Model):
    ordinaryUser = models.ForeignKey('OrdinaryUser', on_delete=models.CASCADE)
    community = models.ForeignKey('Community', on_delete=models.CASCADE)
    role = models.CharField(max_length=20)
    follow_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['ordinaryUser', 'community'], ]


"""
    表名：社群发帖表
    描述：描述一个帖子的基本信息，一个帖子对应一个发帖者和帖子所属的社群
    类型：实体
    说明：帖子的具体内容用Markdown形式存储？
    字段：
    bid                 - 帖子id 主键
    ordinary_user_uid   - 发帖者的id
    community_cid       - 帖子所属社群id
    content_url         - 帖子内容的地址
    likes               - 帖子点赞
    create_time			- 帖子创建时间
    update_time	- 帖子信息最后修改时间
"""


class Blog(models.Model):
    bid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    ordinaryUser = models.ForeignKey('OrdinaryUser', on_delete=models.CASCADE)
    community = models.ForeignKey('Community', on_delete=models.CASCADE)

    content = models.CharField(max_length=2000, null=True)
    likes = models.IntegerField(default=0)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


"""
    帖子评论
    表名：帖子评论表
    描述：描述一个帖子评论基本信息
    类型：实体
    说明：
    字段：

    blog_bid - 帖子主键
    ordinary_user_uid - 用户id(发评论的用户的id)
    likes - 获赞数
    comment - 评论内容
    release_time - 发表时间
"""


class BlogComment(models.Model):
    bcid = models.UUIDField(primary_key=True, default=uuid.uuid4)

    blog = models.ForeignKey('Blog', on_delete=models.CASCADE)
    ordinaryUser = models.ForeignKey('OrdinaryUser', on_delete=models.CASCADE)

    likes = models.IntegerField(default=0)
    comment = models.CharField(max_length=400, default='')
    release_time = models.DateTimeField(auto_now=True)


"""
    登录验证码
"""


class Captcha(models.Model):
    captchaId = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_email = models.EmailField(unique=True)
    captcha = models.CharField(max_length=10)
    expire_time = models.DateTimeField(default=timezone.now)  # 默认设置为当前时间


"""
   消息中心
"""


class Message(models.Model):
    sender = models.ForeignKey(
        'OrdinaryUser',
        on_delete=models.CASCADE,
        related_name='sender',  # 自定义related_name为sender
        null=True
    )
    receiver = models.ForeignKey(
        'OrdinaryUser',
        on_delete=models.CASCADE,
        related_name='receiver'  # 自定义related_name为receiver
    )

    is_system_message = models.BooleanField(default=False)
    has_read = models.BooleanField(default=False)
    message = models.CharField(max_length=400, blank=True)  # 使用blank=True而不是default=''
    send_time = models.DateTimeField(auto_now_add=True)
