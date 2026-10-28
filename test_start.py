import subprocess
import time
p = subprocess.Popen(['py', '-m', 'streamlit', 'run', 'app.py', '--server.headless', 'true', '--server.port', '8505'], 
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
time.sleep(7)
try:
    out = p.stdout.read(1000)
    print(out)
except Exception as e:
    print(e)
p.terminate()
