import subprocess
import sys

p = subprocess.Popen(
    ['buildozer', 'android', 'debug'],
    stdin=subprocess.PIPE,
    stdout=sys.stdout,
    stderr=sys.stderr,
    text=True
)
p.communicate(input='y\n')
sys.exit(p.returncode)