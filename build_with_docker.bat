@echo off
chcp 65001 >nul
echo ========================================
echo   Fantasy RPG Adventure - APK 构建工具
echo ========================================
echo.

:: 检查 Docker 是否可用
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Docker，请先安装 Docker Desktop
    echo 下载地址：https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

echo [信息] Docker 已就绪，开始构建...
echo.

:: 构建镜像
echo [步骤 1/3] 构建 Docker 镜像...
docker build -t fantasy-rpg-builder .
if %errorlevel% neq 0 (
    echo [错误] Docker 镜像构建失败
    pause
    exit /b 1
)

:: 运行构建容器
echo.
echo [步骤 2/3] 运行 APK 构建（这可能需要 10-20 分钟）...
docker run --rm -v "%cd%":/app/output fantasy-rpg-builder
if %errorlevel% neq 0 (
    echo [错误] APK 构建失败
    pause
    exit /b 1
)

:: 检查输出
echo.
echo [步骤 3/3] 检查构建结果...
if exist "bin\*.apk" (
    echo.
    echo ========================================
    echo   ✓ 构建成功！
    echo ========================================
    echo.
    echo APK 文件位置：
    dir /b bin\*.apk
    echo.
    echo 您可以将 APK 文件传输到手机或模拟器进行安装。
) else (
    echo [警告] 未在 bin/ 目录中找到 APK 文件
    echo 请检查构建日志以获取更多信息
)

echo.
pause
