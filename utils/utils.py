import json
import random
import string
import re
from datetime import date, datetime


def checkEmail(email_string) -> bool:
    """
    Checks whether an email string is legal

    :param email_string: an email string
    :return: bool
    """

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(pattern, email_string):
        return True
    else:
        return False


def generateCaptcha(length=6):
    """生成指定长度的随机验证码"""
    captcha = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    return captcha


def checkPassword(password_string) -> bool:
    """
        校验用户密码是否满足规则
        规则：密码长度至少8位，至少包括字母和数字两类字符
    """
    pattern = r'^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{8,}$'
    if re.match(pattern, password_string):
        return True
    else:
        return False


def checkFileExtension(filename: str, allowed_extensions: list[str]) -> str | None:
    """
    :param filename: 待检验的文件名
    :param allowed_extensions: 允许的后缀名列表
    :return: 文件扩展名的类型。文件扩展名不在列表中就返回None
    """
    filename_lower = filename.lower()
    for ext in allowed_extensions:
        if filename_lower.endswith(ext):
            return ext

    return None


def strToDate(date_str: str) -> date | None:
    """
    Convert a string in 'yyyy-MM-dd' format to a datetime.date object.
    If the conversion fails, return None.

    :param date_str: A string representing a date in 'yyyy-MM-dd' format.
    :return: A datetime.date object if conversion is successful, otherwise None.
    """
    try:
        # Convert the string to a datetime.date object
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        # Return None if conversion fails
        return None


def jsonArrayToList(json_array: str) -> list | None:
    """
    将 JSON 数组字符串转换为 Python 列表。

    :param json_array: JSON 数组字符串，如 '[1, 2, 3]'
    :return: Python 列表，解析失败返回 None
    """
    try:
        # 尝试解析 JSON 字符串
        result = json.loads(json_array)
        # 检查解析结果是否为列表
        if isinstance(result, list):
            return result
        else:
            return None
    except json.JSONDecodeError:
        # 解析失败，返回 None
        return None


def get_current_date_components():
    """

    :return: 年月日
    """
    # 获取当前时间
    current_time = datetime.now()
    # 提取年、月、日
    year = current_time.year
    month = current_time.month
    day = current_time.day
    # 将年、月、日转换为整数类型
    year_int = int(year)
    month_int = int(month)
    day_int = int(day)
    return year_int, month_int, day_int


def get_date_seed():
    """

    :return: 年月日
    """
    # 获取当前时间
    current_time = datetime.now()
    # 提取年、月、日
    year = current_time.year
    month = current_time.month
    day = current_time.day
    # 将年、月、日转换为整数类型
    year_int = int(year)
    month_int = int(month)
    day_int = int(day)
    return year_int + month_int + day_int