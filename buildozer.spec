# 奇幻冒险RPG - 安卓打包配置
# 使用 buildozer 打包为 APK

[app]

# (str) 应用标题
title = Fantasy RPG Adventure

# (str) 包名
package.name = fantasyrpg
package.domain = com.game

# (str) 源代码目录
source.dir = .

# (list) 源文件
source.include_exts = py,png,jpg,kv,atlas,wav,mp3

# (str) 应用版本
version = 1.0.0

# (list) Python源码
source.include_patterns = assets/*

# (str) 入口文件
android.entrypoint = org.kivy.android.PythonActivity

# (str) 应用全名
android.package = com.game.fantasyrpg

# (str) Android命名空间
android.namespace = com.game.fantasyrpg

# (int) 目标API
android.api = 31

# (int) 最低API
android.minapi = 24

# (str) 启动器图标（可选）
# icon.filename = %(source.dir)s/data/icon.png

# (str) 横屏/竖屏
orientation = portrait

# (bool) 是否全屏
fullscreen = 0

# (list) 权限
android.permissions = INTERNET,VIBRATE,WAKE_LOCK

# (int) OpenGL ES版本
android.gl_es_version = 2

# (list) 需要打包的库
requirements = python3,kivy,numpy

# (str) 使用的SDL2版本
android.archs = armeabi-v7a,arm64-v8a

# (bool) 是否使用--private方式签名
android.release_artifact = apk

# (bool) 是否调试模式
android.debug = False

# (bool) 签名
android.signing = 1

[buildozer]

# (int) 日志级别
log_level = 2

# (str) 构建输出目录
output_dir = build

# (str) 缓存目录
cache_dir = .cache

# (bool) 是否更新依赖
update_on_build = 1
