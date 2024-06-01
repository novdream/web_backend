# 使用官方Python运行时作为基础镜像
FROM python:3.12

# 设置工作目录
WORKDIR /app
# 将当前目录内容复制到容器的/app目录下
ADD . /app

# 安装requirements.txt中指定的依赖项
RUN pip install --default-timeout=100 --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 开放Django应用的端口
EXPOSE 8000
# 定义容器启动时执行的命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
