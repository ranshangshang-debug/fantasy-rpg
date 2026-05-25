# Fantasy RPG Adventure - Docker 构建镜像
# 基于 Kivy 官方 Buildozer 镜像

FROM kivy/buildozer:latest

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 设置环境变量
ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV ANDROID_NDK_ROOT=/opt/android-ndk

# 构建命令（默认）
CMD ["buildozer", "android", "release"]

# 使用说明：
# 1. 构建：docker build -t fantasy-rpg-builder .
# 2. 运行：docker run -v $(pwd):/app/output fantasy-rpg-builder
# 3. APK 输出位置：bin/*.apk
