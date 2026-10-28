const wallpaper = "file:///usr/share/wallpapers/Avenor/contents/images/1672x941.png"

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
bar.opacity = "translucent"

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
dock.opacity = "translucent"

const launcher = dock.addWidget("org.kde.plasma.kickoff")
launcher.currentConfigGroup = ["General"]
launcher.writeConfig("icon", "avenor")

const tasks = dock.addWidget("org.kde.plasma.icontasks")
tasks.currentConfigGroup = ["General"]
tasks.writeConfig("launchers", [
    "applications:chromium.desktop",
    "applications:org.kde.dolphin.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:systemsettings.desktop"
])
tasks.writeConfig("showOnlyCurrentDesktop", false)

dock.addWidget("org.kde.plasma.trash")
