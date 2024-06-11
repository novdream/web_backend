"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from musicplayer import views_musicplayer as views_mp
from musicplayer import views_producer_center as views_pc
from musicplayer import views_user_center as views_uc
from musicplayer import views_display as views_dp
from musicplayer import views_community as views_cc
from musicplayer import views_message as views_ms
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('email/', views_mp.testEmail),

    # musicplayer 主要对应网站首页部分
    path('api/existEmail/', views_mp.existEmail),
    path('api/existUserName/', views_mp.existUserName),
    path('api/generateCaptcha/', views_mp.generateCaptcha),
    path('api/userRegister/', views_mp.userRegister),
    path('api/userLogin/', views_mp.userLogin),
    path('api/userModifyPassword/', views_mp.userModifyPassword),

    path('api/checkJwtToken/', views_mp.checkJwtToken),
    path('api/updateJwtToken/', views_mp.updateJwtToken),
    path('api/recommendAlbum/', views_mp.recommendAlbum),
    path('api/recommendSong/', views_mp.recommendSong),
    path('api/recommendProducer/', views_mp.recommendProducer),

    # display 信息展示
    path('api/queryProducerById/', views_dp.queryProducerById),
    path('api/querySongByCondition/', views_dp.querySongByCondition),

    path('api/querySongById/', views_dp.querySongById),
    path('api/createSongList/', views_dp.createSongList),
    path('api/modifySongList/', views_dp.modifySongList),
    path('api/querySongList/', views_dp.querySongList),

    path('api/addSongToSongList/', views_dp.addSongToSongList),
    path('api/dropSongFromSongList/', views_dp.dropSongFromSongList),
    path('api/querySongByAlbum/', views_dp.querySongByAlbum),
    path('api/querySongByProducer/', views_dp.querySongByProducer),

    path('api/createSongComment/', views_dp.createSongComment),
    path('api/dropSongComment/', views_dp.dropSongComment),
    path('api/querySongComment/', views_dp.querySongComment),

    path('api/queryProducerByCondition/', views_dp.queryProducerByCondition),
    path('api/followProducer/', views_dp.followProducer),
    path('api/cancelFollowProducer/', views_dp.cancelFollowProducer),

    # 发送sid播放量+1
    path('api/addPlayBack/', views_dp.addPlayBack),


    # userCenter 用户中心
    path('api/editUserInfo/', views_uc.editUserInfo),
    path('api/editUserProfilePicture/', views_uc.editUserProfilePicture),
    path('api/queryUser/', views_uc.queryUser),

    # producerCenter 创作者中心
    path('api/applyProducer/', views_pc.applyProducer),
    path('api/createSong/', views_pc.createSong),
    path('api/modifySong/', views_pc.modifySong),
    path('api/uploadSongAudio/', views_pc.uploadSongAudio),
    path('api/uploadSongLyrics/', views_pc.uploadSongLyrics),

    path('api/createAlbum/', views_pc.createAlbum),
    path('api/modifyAlbum/', views_pc.modifyAlbum),
    path('api/uploadAlbumCover/', views_pc.uploadAlbumCover),

    path('api/querySongOfProducer/', views_pc.querySongOfProducer),
    path('api/queryAlbumOfProducer/', views_pc.queryAlbumOfProducer),
    path('api/queryProducer/', views_pc.queryProducer),

    path('api/queryFansOfProducer/', views_pc.queryFansOfProducer),
    path('api/queryCollaboratedProducer/', views_pc.queryCollaboratedProducer),
    path('api/createSongCollaboration/', views_pc.createSongCollaboration),
    path('api/handleSongCollaboration/', views_pc.handleSongCollaboration),
    path('api/querySongCollaboration/', views_pc.querySongCollaboration),

    # 获取关注歌手人数
    path('api/getNumFollow/', views_pc.getNumFollow),

    # communityCenter 社群中心
    path('api/createCommunity/', views_cc.createCommunity),
    path('api/userFollowCommunity/', views_cc.userFollowCommunity),
    path('api/addSongToCommunity/', views_cc.addSongToCommunity),

    path('api/getUserAllCommunity/', views_cc.getUserAllCommunity),
    path('api/searchCommunity/', views_cc.searchCommunity),
    path('api/showTop5Community/', views_cc.showTop5Community),
    path('api/getDailyBgmOfCommunity/', views_cc.getDailyBgmOfCommunity),

    path('api/showUserTop5Community/', views_cc.showUserTop5Community),
    path('api/queryUserInCommunity/', views_cc.queryUserInCommunity),
    path('api/queryBlogOfCommunity/', views_cc.queryBlogOfCommunity),
    path('api/getBlogComment/', views_cc.getBlogComment),
    path('api/getSongInCommunity/', views_cc.getSongInCommunity),

    path('api/postBlog/', views_cc.postBlog),
    path('api/postBlogComment/', views_cc.postBlogComment),
    path('api/likeBlog/', views_cc.likeBlog),
    path('api/getUserAllBriefBlog/', views_cc.getUserAllBriefBlog),
    path('api/getUserAllBlog/', views_cc.getUserAllBlog),

    # message
    # 发送消息
    path('api/sendMessage/', views_ms.sendMessage),
    path('api/getUserMessage/', views_ms.getUserMessage),
    path('api/getSystemMessage/', views_ms.getSystemMessage),
]
