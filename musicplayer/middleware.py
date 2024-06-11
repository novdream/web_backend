import traceback

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import logging

from utils.result import Result

logger = logging.getLogger('musicplayer')  # 使用你在 settings.py 中定义的 logger 名称


class ExceptionHandlerMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        view_name = '<unknown view>'
        if hasattr(request, 'resolver_match') and request.resolver_match:
            view_func = request.resolver_match.func
            if view_func:
                view_name = view_func.__name__

                # 提取 IP 地址和用户代理
        client_ip = request.META.get('REMOTE_ADDR') or 'unknown'
        user_agent = request.META.get('HTTP_USER_AGENT') or 'unknown'

        extra = {
            'view_name': view_name,
            'client_ip': client_ip,
            'user_agent': user_agent,
            'traceback': str(exception),
            # 你可以添加其他你感兴趣的 request 属性
        }

        # 使用 logger 记录异常，并传递额外的上下文
        logger.error(f'Exception caught', exc_info=True, extra=extra)

        # 返回错误的 JSON 响应
        return JsonResponse(
            Result.failure(
                code=Result.HTTP_STATUS_INTERNAL_SERVER_ERROR,
                message='Internal Server Error'
            )
        )