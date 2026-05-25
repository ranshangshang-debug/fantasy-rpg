# Fantasy RPG Adventure - APK 构建指南

## 项目概述
这是一个使用 Kivy + NumPy 开发的开放式 RPG 游戏，需要打包成 Android APK 文件。

## 文件结构
```
output/
├── main.py                    # 入口文件
├── fantasy_rpg_complete.py    # 游戏主程序
├── music_generator.py         # 音乐生成器
├── buildozer.spec             # Buildozer 配置
├── build_apk.py               # 本地构建脚本
└── .github/
    └── workflows/
        └── build_apk.yml      # GitHub Actions 自动构建
```

## 构建方案

### 方案 1：GitHub Actions 自动构建（推荐）

**优点：** 无需本地配置环境，自动构建，速度快（约 10-15 分钟）

**步骤：**
1. 在 GitHub 创建新仓库
2. 将 `output` 目录下的所有文件推送到仓库
3. 进入仓库的 Actions 页面
4. 选择 "Build Kivy Android APK" 工作流
5. 点击 "Run workflow"
6. 等待构建完成
7. 在 Artifacts 中下载生成的 APK 文件

**快速开始命令：**
```bash
# 初始化 Git 仓库
cd output
git init
git add .
git commit -m "Initial commit: Fantasy RPG Adventure"

# 创建 GitHub 仓库并推送（需要 gh CLI 或手动创建）
gh repo create fantasy-rpg --public --source=. --push
# 或手动：在 github.com 创建仓库后执行
git remote add origin https://github.com/YOUR_USERNAME/fantasy-rpg.git
git push -u origin main
```

---

### 方案 2：Docker 本地构建

**优点：** 完全本地化，无需上传代码到云端

**前置要求：**
- 安装 Docker Desktop
- 确保 Docker 正在运行

**构建步骤：**

1. **创建 Dockerfile（已包含在项目中）：**
   ```dockerfile
   FROM kivy/buildozer:latest
   
   WORKDIR /app
   COPY . .
   
   CMD ["buildozer", "android", "release"]
   ```

2. **运行构建容器：**
   ```bash
   cd output
   docker build -t fantasy-rpg-builder .
   docker run -v $(pwd):/app/output fantasy-rpg-builder
   ```

3. **获取 APK：**
   构建完成后，APK 文件位于 `bin/` 目录下

---

### 方案 3：Linux/WSL2 本地构建

**优点：** 完全控制构建过程

**前置要求：**
- Ubuntu 20.04+ 或 WSL2
- Python 3.8+
- 以下依赖：

**安装依赖：**
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础依赖
sudo apt install -y \
    python3-pip \
    build-essential \
    git \
    zlib1g-dev \
    openjdk-17-jdk \
    autoconf \
    libtool \
    libffi-dev \
    libssl-dev \
    libltdl-dev \
    python3-dev

# 安装 Android SDK 和 NDK
mkdir -p ~/android-sdk ~/android-ndk

# 下载 SDK commandline tools
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip commandlinetools-linux-9477386_latest.zip
mv cmdline-tools ~/android-sdk/cmdline-tools

# 配置环境变量
export ANDROID_SDK_ROOT=~/android-sdk
export ANDROID_NDK_ROOT=~/android-ndk
export PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin

# 接受 SDK 许可证
yes | sdkmanager --licenses > /dev/null 2>&1

# 安装必要组件
sdkmanager "platforms;android-31" "build-tools;33.0.0"

# 下载 NDK (版本 r23c)
wget https://dl.google.com/android/repository/android-ndk-r23c-linux.zip
unzip android-ndk-r23c-linux.zip
mv android-ndk-r23c ~/android-ndk/ndk-r23c
export ANDROID_NDK_ROOT=~/android-ndk/ndk-r23c

# 安装 Buildozer
pip3 install buildozer cython
```

**构建 APK：**
```bash
cd output
buildozer android release
```

**构建时间：** 首次构建约 15-30 分钟（会下载并编译依赖）
**输出位置：** `bin/` 目录

---

### 方案 4：使用在线构建服务

**服务选项：**
1. **GitLab CI** - 类似 GitHub Actions
2. **Codemagic** - 专门用于移动应用构建
3. **AppCenter** - 微软的移动应用构建服务

---

## 安装 APK 到手机/模拟器

### 方法 1：USB 连接
```bash
adb install bin/FantasyRPGAdventure-1.0.0-arm64-v8a-release.apk
```

### 方法 2：通过文件传输
1. 将 APK 文件传输到手机
2. 在手机上打开 APK 文件
3. 允许"安装未知来源应用"
4. 完成安装

### 方法 3：使用 Androws 模拟器
如果使用 Androws 模拟器：
1. 将 APK 文件拖拽到模拟器窗口
2. 或使用模拟器的文件管理器打开 APK
3. 自动安装

---

## 常见问题

### Q: 构建失败提示缺少依赖？
A: 确保 `buildozer.spec` 中的 `requirements` 字段包含所有需要的 Python 库：
```
requirements = python3,kivy,numpy
```

### Q: APK 安装后闪退？
A: 检查 `main.py` 是否正确导入所有模块，确保没有硬编码路径。

### Q: 如何调试？
A: 使用 debug 模式构建，可以通过 `adb logcat` 查看日志：
```bash
buildozer android debug
adb logcat | grep python
```

### Q: 构建太慢怎么办？
A: 
- 使用 GitHub Actions（利用缓存加速）
- 确保网络畅通（需要下载 Android NDK 约 1GB）
- 后续增量构建会快很多

---

## 技术规格

| 项目 | 值 |
|------|-----|
| 应用名称 | Fantasy RPG Adventure |
| 包名 | com.game.fantasyrpg |
| 版本 | 1.0.0 |
| 最低 Android 版本 | 5.0 (API 21) |
| 目标 Android 版本 | 12 (API 31) |
| 支持架构 | armeabi-v7a, arm64-v8a |
| Python 版本 | 3.x (通过 Kivy) |
| 主要依赖 | Kivy, NumPy |

---

## 联系与支持

如遇到问题，请检查：
1. [Buildozer 官方文档](https://buildozer.readthedocs.io/)
2. [Kivy 官方文档](https://kivy.org/doc/stable/)
3. [GitHub Issues](https://github.com/kivy/buildozer/issues)

---

**最后更新：** 2026-05-24
**构建工具版本：** Buildozer 1.6.0
