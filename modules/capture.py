import os
import datetime
from core import config


class CaptureModule:
    def __init__(self, adb):
        self.adb = adb
        os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)

    def screenshot(self):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(config.SCREENSHOT_DIR, f"shift_{ts}.png")
        out, err, code = self.adb.raw("exec-out screencap -p", binary=True, timeout=60)
        if code != 0:
            return None
        with open(path, "wb") as f:
            f.write(out)
        return path

    def screenrecord(self, seconds=10, output=None):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        remote = f"/sdcard/shift_{ts}.mp4"
        self.adb.shell(f"screenrecord --time-limit {seconds} {remote}", timeout=seconds + 10)
        local = output or os.path.join(config.SCREENSHOT_DIR, f"shift_{ts}.mp4")
        self.adb.raw(f"pull {remote} {local}", timeout=120)
        self.adb.shell(f"rm {remote}")
        return local
