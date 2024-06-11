# 这是数据库中的视图。具体实体见项目的sql文件夹createView

from django.db import models


# 创作者视图，由普通用户表的部分信息和创作者账号的部分信息 JOIN 而来
class ProducerView(models.Model):
    pid = models.UUIDField(primary_key=True)
    username = models.CharField(max_length=45)
    profile_picture_url = models.URLField(null=True)
    gender = models.CharField(max_length=1, null=True)
    introduction = models.CharField(max_length=200, null=True)

    ptype = models.CharField(max_length=20, null=True)
    title = models.CharField(max_length=90, null=True)
    authentication = models.CharField(max_length=90, null=True)

    class Meta:
        managed = False  # 指定orm不要管理视图的表
        db_table = 'producer_view'  # 指定视图的名字


# 歌曲列表视图，歌单列表中简要展示歌曲信息的视图
class SongView(models.Model):

    sid = models.UUIDField(primary_key=True)
    sname = models.CharField(max_length=45)
    play_back = models.IntegerField()

    aid = models.UUIDField()
    aname = models.CharField(max_length=45)
    cover_url = models.URLField(null=True)

    pid = models.UUIDField()
    username = models.CharField(max_length=45)

    class Meta:
        managed = False  # 指定orm不要管理视图的表
        db_table = 'song_view'  # 指定视图的名字

