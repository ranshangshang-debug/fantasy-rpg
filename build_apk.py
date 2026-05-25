"""
自动化 Buildozer APK 构建脚本
"""
import subprocess
import sys
import os

def run_buildozer():
    """运行 buildozer 构建 APK"""
    project_dir = r"C:\Users\Admin\AppData\Roaming\Tencent\Marvis\User\oAN1i2fU00XczVwktMysfp6pjeto\workspace\conv_19e58bf3739_1be449a7b623\output"
    
    # 切换到项目目录
    os.chdir(project_dir)
    
    print("开始构建 APK...")
    print(f"项目目录: {project_dir}")
    
    # 尝试使用 android debug 模式（不需要签名）
    try:
        # 使用 subprocess 并自动输入 'y'
        process = subprocess.Popen(
            ['buildozer', 'android', 'debug'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_dir
        )
        
        # 自动确认
        stdout, stderr = process.communicate(input='y\n', timeout=3600)
        
        print("标准输出:")
        print(stdout[-2000:] if len(stdout) > 2000 else stdout)
        
        if stderr:
            print("错误输出:")
            print(stderr[-1000:] if len(stderr) > 1000 else stderr)
            
        return process.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("构建超时")
        process.kill()
        return False
    except Exception as e:
        print(f"构建失败: {e}")
        return False

if __name__ == '__main__':
    success = run_buildozer()
    sys.exit(0 if success else 1)
