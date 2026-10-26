const wallpaper = "file:///usr/share/wallpapers/Avenor/contents/images/3840x2160.svg"

for (const desktop of desktops()) {
    desktop.wallpaperPlugin = "org.kde.image"
    desktop.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"]
    desktop.writeConfig("Image", wallpaper)
}

const bar = new Panel
bar.location = "top"
bar.height = 2 * Math.round(gridUnit * 1.1)
bar.floating = true
bar.lengthMode = "fill"
bar.hiding = "none"

bar.addWidget("org.avenor.wordmark")
bar.addWidget("org.kde.plasma.panelspacer")
bar.addWidget("org.avenor.clock")
bar.addWidget("org.kde.plasma.panelspacer")
bar.addWidget("org.kde.plasma.networkmanagement")
bar.addWidget("org.avenor.batterypill")

const dock = new Panel
dock.location = "bottom"
dock.height = 2 * Math.round(gridUnit * 1.8)
dock.floating = true
dock.lengthMode = "fit"
dock.alignment = "center"
dock.hiding = "none"

const launcher = dock.addWidget("org.kde.plasma.kickoff")
launcher.currentConfigGroup = ["General"]
launcher.writeConfig("icon", "view-app-grid-symbolic")

const tasks = dock.addWidget("org.kde.plasma.icontasks")
tasks.currentConfigGroup = ["General"]
tasks.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:systemsettings.desktop"
])
tasks.writeConfig("showOnlyCurrentDesktop", false)

dock.addWidget("org.kde.plasma.trash")
