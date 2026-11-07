#!/usr/bin/env python3
"""Offline jury installer. Only uses files beside this script and Android adb."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import time

PKG = "ru.mossad.nuclear"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True, help="adb devices serial")
    parser.add_argument("--adb-port", default="5037")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    log = (root / ("installation-" + time.strftime("%Y%m%d-%H%M%S") + ".txt")).open("w")

    def note(message):
        print(message, flush=True)
        log.write(message + "\n")
        log.flush()

    base = ["adb", "-P", args.adb_port, "-s", args.serial]

    def adb(*command, stdin=None, quiet=False):
        note("$ " + " ".join(base + list(command)))
        result = subprocess.run(base + list(command), stdin=stdin,
                                stdout=subprocess.DEVNULL if quiet else subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=240)
        out = (result.stdout or b"").decode("utf-8", "replace").strip()
        err = result.stderr.decode("utf-8", "replace").strip()
        if out:
            note(out)
        if err:
            note(err)
        if result.returncode:
            raise RuntimeError("adb failed: " + str(result.returncode))
        return out

    try:
        # Verify every shipped file before changing anything on the device.
        for line in (root / "SHA256SUMS").read_text().splitlines():
            expected, name = line.split("  ", 1)
            path = root / name
            if not path.resolve().is_relative_to(root) or not path.is_file():
                raise RuntimeError("Invalid/missing bundle file: " + name)
            if digest(path) != expected:
                raise RuntimeError("SHA-256 mismatch: " + name)
            note("HOST SHA256 OK " + name + " " + expected)
        manifest = json.loads((root / "manifest.json").read_text())
        if adb("get-state") != "device":
            raise RuntimeError("Device is not ready")
        if "x86_64" not in adb("shell", "getprop", "ro.product.cpu.abilist").split(","):
            raise RuntimeError("This APK requires Android x86_64")
        if int(adb("shell", "getprop", "ro.build.version.sdk")) < 26:
            raise RuntimeError("Android API 26+ required")
        adb("shell", "cat", "/proc/meminfo")
        adb("shell", "df", "-h", "/data")
        note("Installing APK SHA256 " + manifest["apk"]["sha256"])
        adb("install", "-r", str(root / manifest["apk"]["path"]))
        installed = adb("shell", "pm", "path", PKG)
        if not installed.startswith("package:") or "\n" in installed:
            raise RuntimeError("Unexpected installed APK path")
        actual = adb("shell", "sha256sum", installed.removeprefix("package:")).split()[0]
        if actual != manifest["apk"]["sha256"]:
            raise RuntimeError("Installed APK differs from the bundle APK")
        note("DEVICE APK SHA256 OK " + actual)
        note("RESET: removing all previous private app data")
        if adb("shell", "pm", "clear", PKG) != "Success":
            raise RuntimeError("Could not clear app data")
        for row in manifest["models"]:
            target = row["target"]
            if not re.fullmatch(r"[A-Za-z0-9_./-]+", target) or ".." in PurePosixPath(target).parts:
                raise RuntimeError("Invalid model target")
            target = "files/" + target
            adb("shell", "run-as", PKG, "mkdir", "-p", str(PurePosixPath(target).parent))
            with (root / row["path"]).open("rb") as source:
                # Raw shell v2 waits for the remote writer to exit before hashing.
                # exec-in may return before the device has finished writing.
                adb("shell", "-T", "run-as", PKG, "dd", "of=" + target, "bs=65536", stdin=source)
            actual = adb("shell", "run-as", PKG, "sha256sum", target).split()[0]
            if actual != row["sha256"]:
                raise RuntimeError("Device model SHA-256 mismatch: " + target)
            note("DEVICE SHA256 OK " + target)
        adb("shell", "mkdir", "-p", "/sdcard/Download/Nuclear")
        adb("push", str(root / "samples/jury-speech.wav"), "/sdcard/Download/Nuclear/jury-speech.wav")
        actual = adb("shell", "sha256sum", "/sdcard/Download/Nuclear/jury-speech.wav").split()[0]
        if actual != digest(root / "samples/jury-speech.wav"):
            raise RuntimeError("Device WAV SHA-256 mismatch")
        # adb push leaves a pending FUSE MediaStore row until media scanning.
        # Publish it before opening SAF, so the documented Downloads path works.
        adb("shell", "content", "call", "--uri", "content://media", "--method", "scan_file",
            "--arg", "/storage/emulated/0/Download/Nuclear/jury-speech.wav")
        for attempt in range(20):
            rows = adb("shell", "content", "query", "--uri", "content://media/external/file",
                       "--projection", "_display_name:is_pending:is_download")
            if any("_display_name=jury-speech.wav," in line and "is_pending=0" in line
                   and "is_download=1" in line for line in rows.splitlines()):
                break
            time.sleep(0.25)
        else:
            raise RuntimeError("Sample WAV is not visible in Android Downloads")
        # Both installation and inference need no device network.
        adb("shell", "cmd", "connectivity", "airplane-mode", "enable")
        adb("shell", "svc", "wifi", "disable")
        adb("shell", "svc", "data", "disable")
        if adb("shell", "settings", "get", "global", "airplane_mode_on") != "1":
            raise RuntimeError("Airplane mode was not enabled")
        if adb("shell", "settings", "get", "global", "wifi_on") != "0":
            raise RuntimeError("Wi-Fi was not disabled")
        adb("shell", "am", "start", "-W", "-n", PKG + "/.MainActivity")
        note("SUCCESS: offline models installed and verified; follow JURY.md from step 3")
    finally:
        log.close()


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        sys.exit("INSTALL FAILED: " + str(error))
