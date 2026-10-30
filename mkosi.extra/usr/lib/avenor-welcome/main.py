import configparser
import hashlib
import json
import subprocess
import sys
import threading
from pathlib import Path
from urllib import error, request

from PySide6.QtCore import QObject, Property, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QFont, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

HOME = Path.home()
CONFIG_PATH = HOME / ".config" / "avenor-welcome.conf"
MANGOHUD_PATH = HOME / ".config" / "environment.d" / "90-avenor-mangohud.conf"
FRAMEFX_DIR = HOME / ".local" / "share" / "framefx"
FRAMEFX_APP = FRAMEFX_DIR / "Universal-FrameFX.AppImage"
FRAMEFX_DESKTOP = HOME / ".local" / "share" / "applications" / "universal-framefx.desktop"
HERE = Path(__file__).resolve().parent
ICON = Path("/usr/share/icons/hicolor/128x128/apps/avenor.png")
if not ICON.exists():
    ICON = HERE.parents[1] / "share/icons/hicolor/128x128/apps/avenor.png"
RELEASES_URL = "https://api.github.com/repos/ilikemacos/universal-framefx/releases?per_page=10"
USER_AGENT = "AvenorOS-Welcome"
FRAMEFX_ENTRY = (
    "[Desktop Entry]\nType=Application\nName=Universal FrameFX\n"
    f"Comment=Frame generation for Vulkan games\nExec={FRAMEFX_APP}\n"
    "Icon=applications-games\nTerminal=false\nCategories=Game;Utility;\n"
)

def load_config():
    config = configparser.ConfigParser()
    config["general"] = {"show_at_startup": "true", "seen": "false"}
    config.read(CONFIG_PATH)
    return config

def read_version():
    try:
        for line in Path("/usr/lib/os-release").read_text().splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return "AvenorOS"

class App(QObject):
    pageChanged = Signal()
    showAgainChanged = Signal()
    currentPage = Property(int, lambda self: self.page, notify=pageChanged)
    version = Property(str, lambda self: self.version_text, constant=True)
    iconPath = Property(str, lambda self: QUrl.fromLocalFile(str(ICON)).toString(), constant=True)
    showAgain = Property(bool, lambda self: self.show_again, notify=showAgainChanged)

    def __init__(self, autostart):
        super().__init__()
        self.autostart = autostart
        self.config = load_config()
        self.seen = self.config.getboolean("general", "seen", fallback=False)
        self.show_at_startup = self.config.getboolean("general", "show_at_startup", fallback=True)
        self.page = 0
        self.framefx = None
        self.saved = False
        self.show_again = self.show_at_startup if self.seen or not autostart else False
        self.version_text = read_version()
    @Slot(int)
    def setPage(self, page):
        page = max(0, min(4, page))
        if page == self.page:
            return
        self.page = page
        self.pageChanged.emit()
        if page == 3 and self.framefx:
            self.framefx.load()
    @Slot()
    def nextPage(self): self.setPage(self.page + 1)
    @Slot()
    def backPage(self): self.setPage(self.page - 1)
    @Slot(bool)
    def setShowAgain(self, value):
        if value != self.show_again:
            self.show_again = value
            self.showAgainChanged.emit()
    @Slot()
    def finish(self): QGuiApplication.quit()
    @Slot()
    def save(self):
        if self.saved:
            return
        self.saved = True
        self.seen = self.seen or self.autostart
        self.show_at_startup = self.show_again
        self.config["general"]["seen"] = "true" if self.seen else "false"
        self.config["general"]["show_at_startup"] = "true" if self.show_at_startup else "false"
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CONFIG_PATH.open("w", encoding="utf-8") as handle:
            self.config.write(handle)

class Drivers(QObject):
    changed = Signal()
    gpus = Property("QVariantList", lambda self: self.gpu_list, notify=changed)
    note = Property(str, lambda self: self.prime_note, notify=changed)

    def __init__(self):
        super().__init__()
        self.gpu_list = []
        self.prime_note = ""
        self.refresh()
    @Slot()
    def refresh(self):
        gpus = []
        for device in sorted(Path("/sys/class/drm").glob("card*/device")):
            if not device.parent.name[4:].isdigit():
                continue
            try:
                vendor_id = (device / "vendor").read_text().strip()
                device_id = (device / "device").read_text().strip()
                driver = (device / "driver").readlink().name if (device / "driver").exists() else ""
            except OSError:
                continue
            vendor = {"0x10de": "NVIDIA", "0x1002": "AMD", "0x8086": "Intel"}.get(vendor_id, vendor_id)
            loaded = driver in ("nvidia", "amdgpu", "i915", "xe")
            gpus.append({
                "vendor": vendor,
                "pci": vendor_id + ":" + device_id,
                "driver": driver or "none",
                "loaded": loaded,
            })
        self.gpu_list = gpus
        vendors = {gpu["vendor"] for gpu in gpus}
        self.prime_note = "Games can be started on NVIDIA with prime-run (nvidia-prime is included)." if "NVIDIA" in vendors and len(vendors) > 1 else ""
        self.changed.emit()

class Tweaks(QObject):
    changed = Signal()
    scxEnabled = Property(bool, lambda self: self.scx_enabled, notify=changed)
    scxAvailable = Property(bool, lambda self: self.scx_available, notify=changed)
    mangohudEnabled = Property(bool, lambda self: self.mangohud_enabled, notify=changed)
    gamemodeEnabled = Property(bool, lambda self: self.gamemode_enabled, notify=changed)
    busy = Property(bool, lambda self: self.working, notify=changed)
    error = Property(str, lambda self: self.error_text, notify=changed)

    def __init__(self):
        super().__init__()
        self.scx_enabled = self.mangohud_enabled = self.gamemode_enabled = self.working = False
        self.scx_available = Path("/sys/kernel/sched_ext").exists()
        self.error_text = ""
        self.refresh()
    def unit_enabled(self, command):
        try:
            result = subprocess.run(command, capture_output=True, text=True)
        except OSError:
            return False
        return result.returncode == 0 and result.stdout.strip() == "enabled"
    def mangohud_state(self):
        try:
            return "MANGOHUD=1" in MANGOHUD_PATH.read_text()
        except OSError:
            return False
    @Slot()
    def refresh(self):
        self.scx_enabled = self.unit_enabled(["systemctl", "is-enabled", "avenor-scx.service"])
        self.mangohud_enabled = self.mangohud_state()
        self.gamemode_enabled = self.unit_enabled(["systemctl", "--user", "is-enabled", "gamemoded.service"])
        self.working = False
        self.changed.emit()
    def run_command(self, command):
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout).strip() or "Command failed.")
    def run_in_background(self, action):
        self.working = True
        self.error_text = ""
        self.changed.emit()
        def work():
            error_text = ""
            try:
                action()
            except Exception as exc:
                error_text = str(exc)
            self.error_text = error_text
            self.refresh()
        threading.Thread(target=work, daemon=True).start()
    @Slot(bool)
    def setScx(self, enabled):
        if not self.scx_available or self.working:
            return
        action = "enable" if enabled else "disable"
        self.run_in_background(lambda: self.run_command(["pkexec", "systemctl", action, "--now", "avenor-scx.service"]))
    @Slot(bool)
    def setMangohud(self, enabled):
        if self.working:
            return
        def action():
            if enabled:
                MANGOHUD_PATH.parent.mkdir(parents=True, exist_ok=True)
                MANGOHUD_PATH.write_text("MANGOHUD=1\n")
            elif MANGOHUD_PATH.exists():
                MANGOHUD_PATH.unlink()
        self.run_in_background(action)
    @Slot(bool)
    def setGamemode(self, enabled):
        if self.working:
            return
        action = "enable" if enabled else "disable"
        self.run_in_background(lambda: self.run_command(["systemctl", "--user", action, "--now", "gamemoded.service"]))

class FrameFX(QObject):
    changed = Signal()
    isInstalled = Property(bool, lambda self: self.installed, notify=changed)
    status = Property(str, lambda self: self.state, notify=changed)
    tagName = Property(str, lambda self: self.tag, notify=changed)
    sizeLabel = Property(str, lambda self: self.size_text, notify=changed)
    progressValue = Property(float, lambda self: self.progress, notify=changed)
    messageText = Property(str, lambda self: self.message, notify=changed)

    def __init__(self):
        super().__init__()
        self.installed = FRAMEFX_APP.exists()
        self.state = "installed" if self.installed else "idle"
        self.tag = self.size_text = self.message = self.asset_url = self.sha_url = ""
        self.progress = 0.0
    @Slot()
    def load(self):
        if self.state in ("loading", "ready", "installing") or (self.state == "installed" and self.tag):
            return
        self.state = "loading"
        self.message = ""
        self.changed.emit()
        threading.Thread(target=self.fetch, daemon=True).start()
    def fetch(self):
        try:
            api_request = request.Request(RELEASES_URL, headers={"User-Agent": USER_AGENT})
            with request.urlopen(api_request, timeout=20) as response:
                releases = json.load(response)
            release = next((item for item in releases if "linux-preview" in item.get("tag_name", "")), None)
            assets = release.get("assets", []) if release else []
            asset = next((item for item in assets if item["name"].endswith("-linux-x86_64.AppImage")), None)
            if not asset:
                raise RuntimeError("No Linux preview release with an AppImage was found.")
            checksum = next((item for item in assets if item["name"] == asset["name"] + ".sha256"), None)
            if not checksum:
                raise RuntimeError("No checksum asset was found.")
            self.tag = release["tag_name"]
            self.size_text = "%.1f MB" % (asset["size"] / (1024 * 1024))
            self.asset_url = asset["browser_download_url"]
            self.sha_url = checksum["browser_download_url"]
            self.state = "installed" if self.installed else "ready"
            self.message = ""
        except error.URLError:
            self.state = "offline"
            self.message = "Could not reach GitHub. Check your connection and try again."
        except Exception as exc:
            self.state = "error"
            self.message = str(exc)
        finally:
            self.changed.emit()
    @Slot()
    def install(self):
        if self.state != "ready":
            return
        self.state = "installing"
        self.progress = 0.0
        self.message = ""
        self.changed.emit()
        threading.Thread(target=self.download, daemon=True).start()
    def download(self):
        temporary = FRAMEFX_APP.with_suffix(".part")
        try:
            FRAMEFX_DIR.mkdir(parents=True, exist_ok=True)
            download_request = request.Request(self.asset_url, headers={"User-Agent": USER_AGENT})
            with request.urlopen(download_request, timeout=30) as response, temporary.open("wb") as output:
                total = int(response.headers.get("Content-Length", 0))
                done = 0
                while block := response.read(65536):
                    output.write(block)
                    done += len(block)
                    if total:
                        self.progress = done / total
                        self.changed.emit()
            if self.file_sha256(temporary) != self.fetch_checksum():
                raise RuntimeError("Checksum mismatch.")
            temporary.chmod(0o755)
            temporary.replace(FRAMEFX_APP)
            FRAMEFX_DESKTOP.parent.mkdir(parents=True, exist_ok=True)
            FRAMEFX_DESKTOP.write_text(FRAMEFX_ENTRY)
            self.installed = True
            self.state = "installed"
            self.message = ""
        except Exception as exc:
            temporary.unlink(missing_ok=True)
            self.state = "error"
            self.message = str(exc)
        finally:
            self.changed.emit()
    def fetch_checksum(self):
        checksum_request = request.Request(self.sha_url, headers={"User-Agent": USER_AGENT})
        with request.urlopen(checksum_request, timeout=30) as response:
            text = response.read().decode("utf-8", "replace").strip()
        return text.split()[0].lower()
    def file_sha256(self, path):
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(65536), b""):
                digest.update(block)
        return digest.hexdigest()

def main():
    args = sys.argv[1:]
    def argument(name):
        index = args.index(name) if name in args else -1
        return args[index + 1] if 0 <= index < len(args) - 1 else ""
    autostart = "--autostart" in args
    shot = argument("--shot")
    try:
        page = int(argument("--page") or 0)
    except ValueError:
        page = 0
    config = load_config()
    if autostart and not config.getboolean("general", "show_at_startup", fallback=True):
        return 0
    application = QGuiApplication(sys.argv)
    application.setFont(QFont("Inter"))
    QQuickStyle.setStyle("Basic")
    engine = QQmlApplicationEngine()
    welcome = App(autostart)
    drivers = Drivers()
    tweaks = Tweaks()
    framefx = FrameFX()
    welcome.framefx = framefx
    context = engine.rootContext()
    for name, item in (("app", welcome), ("drivers", drivers), ("tweaks", tweaks), ("framefx", framefx)):
        context.setContextProperty(name, item)
    engine.load(QUrl.fromLocalFile(str(HERE / "Main.qml")))
    if not engine.rootObjects():
        return 1
    welcome.setPage(page)
    application.aboutToQuit.connect(welcome.save)
    if shot:
        window = engine.rootObjects()[0]
        def capture():
            Path(shot).parent.mkdir(parents=True, exist_ok=True)
            window.grabWindow().save(shot)
            application.quit()
        QTimer.singleShot(1500, capture)
    return application.exec()

if __name__ == "__main__":
    sys.exit(main())
