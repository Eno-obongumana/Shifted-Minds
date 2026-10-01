"""APK Analyzer module for SHIFTEDMIND.

Pulls APKs from a connected device and inspects them statically:
permissions, activities, services, receivers, providers, exported
components, signature info, hardcoded URLs, and general manifest data.
"""

import os
import re
import hashlib
from datetime import datetime

from core import config

try:
    from androguard.core.apk import APK as AG_APK
    ANDROGUARD_AVAILABLE = True
except ImportError:
    try:
        from androguard.misc import APK as AG_APK
        ANDROGUARD_AVAILABLE = True
    except ImportError:
        AG_APK = None
        ANDROGUARD_AVAILABLE = False


class APKAnalyzer:
    def __init__(self, adb, package_module=None):
        self.adb = adb
        self.pm = package_module
        os.makedirs(config.DUMP_DIR, exist_ok=True)

    # ---------------- PULL ----------------

    def pull_from_device(self, package):
        """Pull all APK splits for a package from the device into data/dumps/."""
        if not self.pm:
            return None, "PackageModule not attached."

        paths = self.pm.app_path(package)
        if not paths:
            return None, f"No APK paths for {package}"

        saved = []
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_dir = os.path.join(config.DUMP_DIR, f"{package}_{ts}")
        os.makedirs(target_dir, exist_ok=True)

        for remote in paths:
            filename = os.path.basename(remote)
            local = os.path.join(target_dir, filename)
            _, err, code = self.adb.raw(f"pull {remote} {local}", timeout=180)
            if code == 0 and os.path.exists(local):
                saved.append(local)

        if not saved:
            return None, "Pull failed for all splits."
        return target_dir, saved

    # ---------------- LOCAL FILE ANALYZE ----------------

    def _load(self, apk_path):
        if not ANDROGUARD_AVAILABLE:
            raise RuntimeError("androguard not installed. Run: pip install androguard")
        if not os.path.exists(apk_path):
            raise FileNotFoundError(apk_path)
        return AG_APK(apk_path)

    def info(self, apk_path):
        a = self._load(apk_path)
        return {
            "Package":      a.get_package() or "?",
            "App name":     a.get_app_name() or "?",
            "Version name": a.get_androidversion_name() or "?",
            "Version code": a.get_androidversion_code() or "?",
            "Min SDK":      a.get_min_sdk_version() or "?",
            "Target SDK":   a.get_target_sdk_version() or "?",
            "Main activity": a.get_main_activity() or "?",
            "Signed":       "yes" if a.is_signed() else "no",
        }

    def permissions(self, apk_path):
        a = self._load(apk_path)
        return sorted(a.get_permissions() or [])

    def activities(self, apk_path):
        a = self._load(apk_path)
        return sorted(a.get_activities() or [])

    def services(self, apk_path):
        a = self._load(apk_path)
        return sorted(a.get_services() or [])

    def receivers(self, apk_path):
        a = self._load(apk_path)
        return sorted(a.get_receivers() or [])

    def providers(self, apk_path):
        a = self._load(apk_path)
        return sorted(a.get_providers() or [])

    def exported(self, apk_path):
        """Return dict of component type -> list of exported components.

        Reads AndroidManifest.xml directly via androguard's parser.
        """
        a = self._load(apk_path)
        result = {
            "activities": [],
            "services":   [],
            "receivers":  [],
            "providers":  [],
        }

        xml = a.get_android_manifest_axml().get_xml()
        if xml is None:
            return result

        ns = "{http://schemas.android.com/apk/res/android}"

        def walk(node, kind, tag):
            for child in node:
                if child.tag == tag:
                    name = child.get(ns + "name", "?")
                    exported = child.get(ns + "exported")
                    has_filter = any(
                        c.tag.endswith("intent-filter") for c in child
                    )
                    # Android: exported defaults to True if intent-filter present (pre-31)
                    if exported == "true" or (exported is None and has_filter):
                        result[kind].append(name)
                walk(child, kind, tag)

        root = xml
        walk(root, "activities", "activity")
        walk(root, "services",   "service")
        walk(root, "receivers",  "receiver")
        walk(root, "providers",  "provider")
        return result

    def certificate(self, apk_path):
        a = self._load(apk_path)
        try:
            certs = a.get_certificates()
            if not certs:
                return {"signed": False}
            cert = certs[0]
            return {
                "signed":          True,
                "subject":         str(cert.subject.human_friendly),
                "issuer":          str(cert.issuer.human_friendly),
                "serial":          str(cert.serial_number),
                "sha1":            cert.sha1_fingerprint.replace(" ", "").lower(),
                "sha256":          cert.sha256_fingerprint.replace(" ", "").lower(),
                "not_before":      str(cert.not_valid_before),
                "not_after":       str(cert.not_valid_after),
            }
        except Exception as e:
            return {"signed": False, "error": str(e)}

    def hardcoded_urls(self, apk_path, limit=200):
        """Scan raw DEX strings for http(s) URLs. Cheap and cheerful."""
        a = self._load(apk_path)
        pattern = re.compile(rb"https?://[A-Za-z0-9\.\-_/:%\?=&#]+")
        found = set()

        for dex in a.get_all_dex():
            for m in pattern.finditer(dex):
                url = m.group(0).decode("utf-8", errors="ignore")
                if len(url) < 12:
                    continue
                found.add(url)
                if len(found) >= limit:
                    break
            if len(found) >= limit:
                break
        return sorted(found)

    def file_hashes(self, apk_path):
        h = {"md5": hashlib.md5(), "sha1": hashlib.sha1(), "sha256": hashlib.sha256()}
        size = 0
        with open(apk_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                size += len(chunk)
                for k in h:
                    h[k].update(chunk)
        return {
            "size_bytes": size,
            "md5":     h["md5"].hexdigest(),
            "sha1":    h["sha1"].hexdigest(),
            "sha256":  h["sha256"].hexdigest(),
        }
