class PackageModule:
    def __init__(self, adb):
        self.adb = adb

    def list_packages(self, third_party_only=True):
        flag = "-3" if third_party_only else ""
        out, _, _ = self.adb.shell(f"pm list packages {flag}")
        return sorted(
            line.replace("package:", "").strip()
            for line in out.splitlines()
            if line.strip().startswith("package:")
        )

    def search(self, keyword, third_party_only=True):
        return [p for p in self.list_packages(third_party_only) if keyword.lower() in p.lower()]

    def app_path(self, package):
        out, _, _ = self.adb.shell(f"pm path {package}")
        return [line.replace("package:", "").strip() for line in out.splitlines() if line.strip()]

    def launch(self, package):
        out, err, code = self.adb.shell(
            f"monkey -p {package} -c android.intent.category.LAUNCHER 1"
        )
        return code == 0

    def stop(self, package):
        out, err, code = self.adb.shell(f"am force-stop {package}")
        return code == 0

    def clear_data(self, package):
        out, err, code = self.adb.shell(f"pm clear {package}")
        return "Success" in out

    def uninstall(self, package):
        out, err, code = self.adb.raw(f"uninstall {package}")
        return "Success" in out
