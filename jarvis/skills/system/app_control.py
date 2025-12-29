# actions/system/app_control.py
import subprocess

def open_application(name):
    try:
        subprocess.Popen([name])
        return True
    except:
        return False
