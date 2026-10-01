import subprocess
import shlex


class LogcatModule:
    def __init__(self, adb):
        self.adb = adb

    def dump(self, lines=200, filter_str=None):
        cmd = self.adb.base + ["logcat", "-d", "-t", str(lines)]
        if filter_str:
            cmd += shlex.split(filter_str)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout

    def clear(self):
        self.adb.raw("logcat -c")

    def stream(self, filter_str=None):
        cmd = self.adb.base + ["logcat"]
        if filter_str:
            cmd += shlex.split(filter_str)
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1)
