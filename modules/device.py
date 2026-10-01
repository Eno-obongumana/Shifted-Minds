class DeviceModule:
    def __init__(self, adb):
        self.adb = adb

    def info(self):
        keys = {
            "Model": "ro.product.model",
            "Manufacturer": "ro.product.manufacturer",
            "Android": "ro.build.version.release",
            "SDK": "ro.build.version.sdk",
            "Serial": "ro.serialno",
            "ABI": "ro.product.cpu.abi",
            "Build": "ro.build.display.id",
        }
        return {label: self.adb.getprop(key) or "Unknown" for label, key in keys.items()}

    def battery(self):
        out, _, _ = self.adb.shell("dumpsys battery")
        data = {}
        for line in out.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
        return data

    def screen_state(self):
        out, _, _ = self.adb.shell("dumpsys power | grep 'mWakefulness'")
        return out.strip() or "Unknown"
