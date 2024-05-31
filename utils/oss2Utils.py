import oss2
from django.core.files.uploadedfile import TemporaryUploadedFile
from oss2.models import PutObjectResult
from django.conf import settings


class OSS2Utils:
    bucket_name = 'tjmusicplayer'
    endpoint_profile = 'https://'
    endpoint = 'oss-cn-hangzhou.aliyuncs.com'

    @staticmethod
    def get_auth():
        aliyun_access_key_id = settings.ALIYUN_ACCESS_KEY_ID
        aliyun_secret_access_key = settings.ALIYUN_ACCESS_KEY_SECRET
        auth = oss2.Auth(aliyun_access_key_id, aliyun_secret_access_key)
        return auth

    @staticmethod
    def get_bucket():
        auth = OSS2Utils.get_auth()
        bucket = oss2.Bucket(
            auth=auth,
            endpoint=OSS2Utils.endpoint_profile + OSS2Utils.endpoint,
            bucket_name=OSS2Utils.bucket_name,
        )
        return bucket

    @staticmethod
    def upload(request_file, oss_filename, oss_folder: list[str]) -> str | None:
        """

        :param request_file: POST请求中获取的文件
        :param oss_filename: 一般是经过uuid处理后的文件
        :param oss_folder:  路径列表，如['user','profilePicture']表示
                oss 中的存储路径为 /user/profilePicture
        :return: 文件上传后的url路径
        """
        oss_key = '{}/{}'.format(
            '/'.join(oss_folder),
            oss_filename,
        )

        bucket = OSS2Utils.get_bucket()

        if isinstance(request_file, TemporaryUploadedFile):
            result = bucket.put_object_from_file(
                key=oss_key,
                filename=request_file.temporary_file_path(),
            )
        else:
            result = bucket.put_object(
                key=oss_key,
                data=request_file.read(),
            )

        if isinstance(result, PutObjectResult):
            return '{}{}.{}/{}'.format(
                OSS2Utils.endpoint_profile,  # https://
                OSS2Utils.bucket_name,  # music_player
                # .
                OSS2Utils.endpoint,
                # /
                oss_key,
            )
        else:
            return None
