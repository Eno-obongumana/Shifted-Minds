class FileModule:
    def __init__(self, adb):
        self.adb = adb

    def ls(self, path="/sdcard"):
        out, _, _ = self.adb.shell(f"ls -la {path}")
        return out

    def pull(self, remote, local):
        _, err, code = self.adb.raw(f"pull {remote} {local}", timeout=120)
        return code == 0, err

    def push(self, local, remote):
        _, err, code = self.adb.raw(f"push {local} {remote}", timeout=120)
        return code == 0, err
