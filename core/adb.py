import subprocess
import shlex


class ADB:
    def __init__(self, serial=None, logger=None):
        self.serial = serial
        self.logger = logger
        self.base = ["adb"] + (["-s", serial] if serial else [])

    def _log(self, msg):
        if self.logger:
            self.logger.log(msg)

    def raw(self, command, timeout=30, binary=False):
        cmd = self.base + shlex.split(command)
        self._log(f"$ {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout,
                text=not binary,
            )
            return result.stdout, result.stderr, result.returncode
        except FileNotFoundError:
            return "", "ADB not found. Install platform-tools.", -1
        except subprocess.TimeoutExpired:
            return "", "Command timed out", -1

    def shell(self, command, timeout=30):
        return self.raw(f"shell {command}", timeout=timeout)

    def devices(self):
        out, _, _ = self.raw("devices")
        devs = []
        for line in out.splitlines()[1:]:
            line = line.strip()
            if line and "\t" in line:
                serial, state = line.split("\t")
                if state == "device":
                    devs.append(serial)
        return devs

    def getprop(self, key):
        out, _, _ = self.shell(f"getprop {key}")
        return out.strip()
