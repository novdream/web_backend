from musicplayer import models


def existEmailCheck(email_str) -> bool:
    emailCount = models.OrdinaryUser.objects.filter(email=email_str).count()
    return emailCount != 0


def existUserCheck(username_str) -> bool:
    userCount = models.OrdinaryUser.objects.filter(username=username_str).count()
    return userCount != 0


def checkUserLogin(email, password):
    """

    :param email: 输入的邮箱
    :param password: 输入的密码
    :return: 如果成功登录则返回该用户对象，否则返回None
    """

    user = models.OrdinaryUser.objects.filter(email=email, password=password).first()
    return user
