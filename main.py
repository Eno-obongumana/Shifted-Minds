import sys
import os
from core import config
from core.adb import ADB
from core.logger import SessionLogger
from ui import banner, widgets, menu
from modules.device import DeviceModule
from modules.packages import PackageModule
from modules.network import NetworkModule
from modules.files import FileModule
from modules.logcat import LogcatModule
from modules.capture import CaptureModule
from modules.apk_menu import apk_menu


def ensure_dirs():
    for d in (config.DATA_DIR, config.SCREENSHOT_DIR, config.LOG_DIR, config.DUMP_DIR):
        os.makedirs(d, exist_ok=True)


def pick_device(adb):
    devs = adb.devices()
    if not devs:
        widgets.err("No ADB devices found. Enable USB debugging and plug in.")
        return None
    if len(devs) == 1:
        widgets.ok(f"Using device: {devs[0]}")
        return devs[0]
    widgets.table("Devices", ["#", "Serial"], [[i + 1, d] for i, d in enumerate(devs)])
    choice = widgets.ask("Pick device #")
    try:
        return devs[int(choice) - 1]
    except (ValueError, IndexError):
        widgets.err("Invalid selection.")
        return None


def packages_menu(adb):
    pm = PackageModule(adb)
    while True:
        widgets.panel(
            "[1] List (3rd-party)\n"
            "[2] List (all)\n"
            "[3] Search\n"
            "[4] Launch\n"
            "[5] Force-stop\n"
            "[6] Clear data\n"
            "[7] Uninstall\n"
            "[0] Back",
            title="Packages"
        )
        c = widgets.ask("choice", "0")
        if c == "0":
            return
        elif c == "1":
            widgets.table("Packages (3rd-party)", ["Package"], [[p] for p in pm.list_packages(True)])
        elif c == "2":
            widgets.table("Packages (all)", ["Package"], [[p] for p in pm.list_packages(False)])
        elif c == "3":
            kw = widgets.ask("keyword")
            widgets.table(f"Matches: {kw}", ["Package"], [[p] for p in pm.search(kw)])
        elif c == "4":
            pkg = widgets.ask("package")
            widgets.ok("launched") if pm.launch(pkg) else widgets.err("failed")
        elif c == "5":
            pkg = widgets.ask("package")
            widgets.ok("stopped") if pm.stop(pkg) else widgets.err("failed")
        elif c == "6":
            pkg = widgets.ask("package")
            if widgets.confirm(f"Clear data for {pkg}?"):
                widgets.ok("cleared") if pm.clear_data(pkg) else widgets.err("failed")
        elif c == "7":
            pkg = widgets.ask("package")
            if widgets.confirm(f"Uninstall {pkg}?"):
                widgets.ok("uninstalled") if pm.uninstall(pkg) else widgets.err("failed")


def network_menu(adb):
    nm = NetworkModule(adb)
    while True:
        widgets.panel(
            "[1] IP addresses\n"
            "[2] WiFi info\n"
            "[3] Open ports\n"
            "[4] Ping host\n"
            "[0] Back",
            title="Network"
        )
        c = widgets.ask("choice", "0")
        if c == "0":
            return
        elif c == "1":
            widgets.panel("\n".join(nm.ip_addresses()) or "none", title="IPs")
        elif c == "2":
            widgets.panel(nm.wifi_info() or "none", title="WiFi")
        elif c == "3":
            widgets.table("Listening ports", ["Port"], [[p] for p in nm.open_ports()])
        elif c == "4":
            host = widgets.ask("host", "8.8.8.8")
            widgets.panel(nm.ping(host), title=f"ping {host}")


def files_menu(adb):
    fm = FileModule(adb)
    while True:
        widgets.panel("[1] ls\n[2] pull\n[3] push\n[0] Back", title="Files")
        c = widgets.ask("choice", "0")
        if c == "0":
            return
        elif c == "1":
            path = widgets.ask("path", "/sdcard")
            widgets.panel(fm.ls(path), title=path)
        elif c == "2":
            remote = widgets.ask("remote path")
            local = widgets.ask("local path", "./pulled.bin")
            ok, err = fm.pull(remote, local)
            widgets.ok(f"pulled → {local}") if ok else widgets.err(err)
        elif c == "3":
            local = widgets.ask("local path")
            remote = widgets.ask("remote path", "/sdcard/")
            ok, err = fm.push(local, remote)
            widgets.ok(f"pushed → {remote}") if ok else widgets.err(err)


def capture_menu(adb):
    cm = CaptureModule(adb)
    while True:
        widgets.panel("[1] Screenshot\n[2] Record 10s\n[0] Back", title="Capture")
        c = widgets.ask("choice", "0")
        if c == "0":
            return
        elif c == "1":
            p = cm.screenshot()
            widgets.ok(f"saved → {p}") if p else widgets.err("screenshot failed")
        elif c == "2":
            secs = int(widgets.ask("seconds", "10"))
            p = cm.screenrecord(secs)
            widgets.ok(f"saved → {p}")


def logcat_menu(adb):
    lm = LogcatModule(adb)
    while True:
        widgets.panel(
            "[1] Dump last 200\n[2] Dump with filter\n[3] Clear\n[0] Back",
            title="Logcat"
        )
        c = widgets.ask("choice", "0")
        if c == "0":
            return
        elif c == "1":
            widgets.code(lm.dump(200))
        elif c == "2":
            f = widgets.ask("filter", "*:E")
            widgets.code(lm.dump(500, f))
        elif c == "3":
            lm.clear()
            widgets.ok("logcat cleared")


def main():
    ensure_dirs()
    banner.show()
    logger = SessionLogger()
    adb = ADB(logger=logger)
    serial = pick_device(adb)
    if not serial:
        return
    adb = ADB(serial=serial, logger=logger)
    dm = DeviceModule(adb)

    while True:
        c = menu.main_menu()
        if c == "0":
            widgets.info("SHIFTEDMIND shutting down…")
            logger.close()
            return
        elif c == "1":
            widgets.kv("Device Info", dm.info())
        elif c == "2":
            widgets.kv("Battery", dm.battery())
            widgets.panel(dm.screen_state(), title="Screen State")
        elif c == "3":
            packages_menu(adb)
        elif c == "4":
            network_menu(adb)
        elif c == "5":
            files_menu(adb)
        elif c == "6":
            capture_menu(adb)
        elif c == "7":
            logcat_menu(adb)
        elif c == "8":
            new = pick_device(ADB())
            if new:
                adb = ADB(serial=new, logger=logger)
                dm = DeviceModule(adb)
        elif c == "9":
            apk_menu(adb, PackageModule(adb))
        else:
            widgets.err("Unknown option.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupted.")
        sys.exit(0)
