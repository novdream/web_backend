import time
from datetime import datetime, timedelta
import jwt

from musicplayer import models
from django.conf import settings


def generateJwtToken(ordinary_user, hours=2):
    """
    :param ordinary_user: Model层定义的普通用户
    :param hours: 令牌的过期时间，默认两小时
    :return: 编码后的jwt令牌
    """
    #  获取JWT 密钥
    jwt_secret = settings.JWT_SECRET_KEY

    # 计算过期时间的时间戳
    expiration_time = time.time() + timedelta(hours=hours).total_seconds()

    # 创建payload
    payload = {
        'uid': str(ordinary_user.uid),
        'email': str(ordinary_user.email),
        'exp': int(expiration_time),  # 使用 'exp' 字段表示过期时间，这是JWT的一个标准字段
    }

    # 编码JWT
    encode_jwt = jwt.encode(
        payload=payload,
        key=jwt_secret,
        algorithm='HS256'
    )

    return encode_jwt


def decodeJwtToken(jwt_token: str):
    """
    :param jwt_token: 前端带来的令牌字符串
    :return: 如果令牌正确则返回ordinaryUser对象，否则返回None
    """

    #  获取JWT 密钥
    jwt_secret = settings.JWT_SECRET_KEY

    try:
        decoded_token = jwt.decode(
            jwt=jwt_token,
            key=jwt_secret,
            algorithms=['HS256'],
        )

        curr_time = time.time()
        expiration_time = decoded_token['exp']

        if curr_time > expiration_time:
            return None

        ordinary_user = models.OrdinaryUser.objects.filter(
            uid=decoded_token['uid'],
            email=decoded_token['email']
        ).first()

        return ordinary_user

    except jwt.DecodeError:
        return None

    except Exception as e:
        return None
