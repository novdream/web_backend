from http import client


class Result(object):
    # 200 请求成功
    HTTP_STATUS_OK = client.OK

    # 400 请求失败，责任在客户端
    HTTP_STATUS_BAD_REQUEST = client.BAD_REQUEST

    # 401 未认证
    HTTP_STATUS_UNAUTHORIZED = client.UNAUTHORIZED

    # 403 禁止访问
    HTTP_STATUS_FORBIDDEN = client.FORBIDDEN

    # 404 没有资源
    HTTP_STATUS_NOT_FOUND = client.NOT_FOUND

    # 405 请求方式错误
    HTTP_STATUS_METHOD_NOT_ALLOWED = client.METHOD_NOT_ALLOWED

    # 406 请求不被接受
    HTTP_STATUS_NOT_ACCEPTABLE = client.NOT_ACCEPTABLE

    # 409 冲突
    HTTP_STATUS_CONFLICT = client.CONFLICT

    # 500 服务器异常
    HTTP_STATUS_INTERNAL_SERVER_ERROR = client.INTERNAL_SERVER_ERROR

    def __init__(self, code, message, obj):
        self.resultDict = {'code': code, 'message': message, 'obj': obj}

    def getResult(self):
        return self.resultDict

    @staticmethod
    def success(obj=None):
        return Result(client.OK, 'Success', obj).getResult()

    @staticmethod
    def failure(code, message, obj=None):
        return Result(code, message, obj).getResult()
