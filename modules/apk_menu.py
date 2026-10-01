"""Interactive menu for the APK Analyzer."""

import os
from ui import widgets
from modules.apk import APKAnalyzer, ANDROGUARD_AVAILABLE


HELP = (
    "[1] Pull APK from device\n"
    "[2] Analyze existing APK file (path)\n"
    "[3] List permissions\n"
    "[4] List activities\n"
    "[5] List exported components\n"
    "[6] List services / receivers / providers\n"
    "[7] Search hardcoded URLs\n"
    "[8] Certificate info\n"
    "[9] File hashes (MD5/SHA1/SHA256)\n"
    "[0] Back"
)


def _require_androguard():
    if not ANDROGUARD_AVAILABLE:
        widgets.err("androguard not installed. Run: pip install androguard")
        return False
    return True


def apk_menu(adb, package_module):
    """Interactive APK analyzer loop.

    adb: ADB instance
    package_module: PackageModule instance (for pulling APKs)
    """
    analyzer = APKAnalyzer(adb, package_module)
    current_apk = None

    while True:
        widgets.panel(HELP, title="APK Analyzer")
        if current_apk:
            widgets.info(f"target: {current_apk}")

        c = widgets.ask("apk", "0")

        if c == "0":
            return

        # -------- Pull from device --------
        elif c == "1":
            pkg = widgets.ask("package")
            if not pkg:
                continue
            widgets.info(f"pulling {pkg} …")
            target_dir, saved = analyzer.pull_from_device(pkg)
            if not target_dir:
                widgets.err(str(saved))
                continue
            widgets.ok(f"pulled {len(saved)} file(s) → {target_dir}")
            # Pick the base.apk if present
            base = os.path.join(target_dir, "base.apk")
            if os.path.exists(base):
                current_apk = base
            else:
                current_apk = saved[0]
            widgets.ok(f"loaded: {current_apk}")

        # -------- Point at an existing file --------
        elif c == "2":
            path = widgets.ask("apk path")
            if path and os.path.exists(path):
                current_apk = path
                widgets.ok(f"loaded: {path}")
            else:
                widgets.err("file not found")

        # -------- Everything below needs a loaded APK --------
        elif c in {"3", "4", "5", "6", "7", "8", "9"}:
            if not current_apk:
                widgets.err("no APK loaded — use [1] or [2] first")
                continue
            if not _require_androguard():
                continue

            try:
                if c == "3":
                    perms = analyzer.permissions(current_apk)
                    widgets.table(
                        f"Permissions ({len(perms)})",
                        ["Permission"],
                        [[p] for p in perms],
                    )

                elif c == "4":
                    acts = analyzer.activities(current_apk)
                    widgets.table(
                        f"Activities ({len(acts)})",
                        ["Activity"],
                        [[a] for a in acts],
                    )

                elif c == "5":
                    exp = analyzer.exported(current_apk)
                    total = sum(len(v) for v in exp.values())
                    if total == 0:
                        widgets.info("No exported components found.")
                        continue
                    for kind, items in exp.items():
                        if items:
                            widgets.table(
                                f"Exported {kind} ({len(items)})",
                                [kind[:-1].capitalize()],
                                [[i] for i in items],
                                color="bright_red",
                            )

                elif c == "6":
                    for label, fn in (
                        ("Services",  analyzer.services),
                        ("Receivers", analyzer.receivers),
                        ("Providers", analyzer.providers),
                    ):
                        items = fn(current_apk)
                        if items:
                            widgets.table(
                                f"{label} ({len(items)})",
                                [label[:-1]],
                                [[i] for i in items],
                            )

                elif c == "7":
                    urls = analyzer.hardcoded_urls(current_apk)
                    if not urls:
                        widgets.info("No URLs found.")
                    else:
                        widgets.table(
                            f"Hardcoded URLs ({len(urls)})",
                            ["URL"],
                            [[u] for u in urls],
                            color="bright_yellow",
                        )

                elif c == "8":
                    info = analyzer.certificate(current_apk)
                    widgets.kv("Certificate", info)

                elif c == "9":
                    info = analyzer.file_hashes(current_apk)
                    widgets.kv("Hashes", info)

            except Exception as e:
                widgets.err(f"analysis failed: {e}")

        else:
            widgets.err("Unknown option.")
