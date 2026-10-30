import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 860
    height: 560
    minimumWidth: 860
    minimumHeight: 560
    visible: true
    title: "AvenorOS Welcome"
    color: root.canvasColor

    readonly property color canvasColor: "#faf8f5"
    readonly property color cardColor: "#ffffff"
    readonly property color ink: "#2e2a26"
    readonly property color mutedInk: "#807870"
    readonly property color accentColor: "#607296"
    readonly property color positiveColor: "#5e8c61"
    readonly property color negativeColor: "#c2410c"
    readonly property color lineColor: "#1f2e2a26"
    readonly property color softColor: "#f1ede7"
    readonly property var steps: ["Welcome", "Drivers", "Gaming tweaks", "FrameFX", "Finish"]

    component ActionButton: Button {
        id: control
        property bool primary: false
        implicitWidth: 104
        implicitHeight: 38
        background: Rectangle {
            radius: 8
            color: !control.enabled ? "#eeeae5" : control.primary ? "#607296" : "#ffffff"
            border.width: control.primary ? 0 : 1
            border.color: "#1f2e2a26"
        }
        contentItem: Text {
            text: control.text
            color: !control.enabled ? "#b3aca4" : control.primary ? "#ffffff" : "#2e2a26"
            font.family: "Inter"
            font.pixelSize: 14
            font.weight: Font.Medium
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }

    component Toggle: Item {
        id: control
        property bool value: false
        property bool available: true
        signal toggled(bool state)
        implicitWidth: 44
        implicitHeight: 24
        Rectangle {
            anchors.fill: parent
            radius: 12
            color: !control.available ? "#e8e3dd" : control.value ? "#607296" : "#d9d3cb"
        }
        Rectangle {
            width: 18
            height: 18
            radius: 9
            y: 3
            x: control.value ? 23 : 3
            color: "#ffffff"
            Behavior on x { NumberAnimation { duration: 120 } }
        }
        MouseArea {
            anchors.fill: parent
            enabled: control.available
            cursorShape: control.available ? Qt.PointingHandCursor : Qt.ArrowCursor
            onClicked: control.toggled(!control.value)
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.preferredWidth: 236
            Layout.fillHeight: true
            color: "transparent"

            Rectangle {
                anchors.right: parent.right
                width: 1
                height: parent.height
                color: root.lineColor
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 6

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    Image {
                        source: app.iconPath
                        sourceSize.width: 30
                        sourceSize.height: 30
                        fillMode: Image.PreserveAspectFit
                    }
                    Text {
                        text: "AvenorOS"
                        color: root.ink
                        font.pixelSize: 15
                        font.weight: Font.DemiBold
                    }
                    Item { Layout.fillWidth: true }
                }

                Item { Layout.preferredHeight: 16 }

                Repeater {
                    model: root.steps.length
                    delegate: Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: 46
                        radius: 8
                        color: app.currentPage === index ? Qt.rgba(0.376, 0.447, 0.588, 0.10) : "transparent"
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 10
                            anchors.rightMargin: 10
                            spacing: 10
                            Rectangle {
                                implicitWidth: 24
                                implicitHeight: 24
                                radius: 12
                                color: app.currentPage === index ? root.accentColor : root.softColor
                                Text {
                                    anchors.centerIn: parent
                                    text: index + 1
                                    color: app.currentPage === index ? "#ffffff" : root.mutedInk
                                    font.pixelSize: 12
                                    font.weight: Font.DemiBold
                                }
                            }
                            Text {
                                Layout.fillWidth: true
                                text: root.steps[index]
                                color: app.currentPage === index ? root.ink : root.mutedInk
                                font.pixelSize: 14
                                font.weight: app.currentPage === index ? Font.DemiBold : Font.Normal
                                elide: Text.ElideRight
                            }
                        }
                    }
                }

                Item { Layout.fillHeight: true }

                Text {
                    Layout.fillWidth: true
                    text: app.version
                    color: root.mutedInk
                    font.pixelSize: 11
                    elide: Text.ElideRight
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 28
                spacing: 16

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: root.cardColor
                    radius: 12
                    border.width: 1
                    border.color: root.lineColor

                    StackLayout {
                        anchors.fill: parent
                        anchors.margins: 28
                        currentIndex: app.currentPage

                        ColumnLayout {
                            spacing: 14
                            Item { Layout.fillHeight: true }
                            Image {
                                Layout.alignment: Qt.AlignHCenter
                                source: app.iconPath
                                sourceSize.width: 96
                                sourceSize.height: 96
                                fillMode: Image.PreserveAspectFit
                            }
                            Text {
                                Layout.fillWidth: true
                                text: "Welcome to AvenorOS"
                                horizontalAlignment: Text.AlignHCenter
                                color: root.ink
                                font.pixelSize: 28
                                font.weight: Font.DemiBold
                            }
                            Text {
                                Layout.fillWidth: true
                                text: "A quiet, private Linux built for laptops."
                                horizontalAlignment: Text.AlignHCenter
                                color: root.mutedInk
                                font.pixelSize: 14
                            }
                            Text {
                                Layout.fillWidth: true
                                text: app.version
                                horizontalAlignment: Text.AlignHCenter
                                color: root.mutedInk
                                font.pixelSize: 13
                            }
                            Item { Layout.fillHeight: true }
                        }

                        ColumnLayout {
                            spacing: 12
                            Text {
                                text: "Drivers"
                                color: root.ink
                                font.pixelSize: 22
                                font.weight: Font.DemiBold
                            }
                            Text {
                                Layout.fillWidth: true
                                text: "Graphics hardware detected in this system."
                                color: root.mutedInk
                                font.pixelSize: 13
                            }
                            Repeater {
                                model: drivers.gpus
                                delegate: Rectangle {
                                    Layout.fillWidth: true
                                    implicitHeight: modelData.loaded ? 68 : 84
                                    color: root.canvasColor
                                    radius: 8
                                    border.width: 1
                                    border.color: root.lineColor
                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        spacing: 2
                                        RowLayout {
                                            Layout.fillWidth: true
                                            spacing: 10
                                            Text {
                                                Layout.fillWidth: true
                                                text: modelData.vendor + " GPU"
                                                color: root.ink
                                                font.pixelSize: 14
                                                font.weight: Font.DemiBold
                                                elide: Text.ElideRight
                                            }
                                            Text {
                                                text: modelData.loaded ? "Driver loaded" : "Not loaded"
                                                color: modelData.loaded ? root.positiveColor : root.negativeColor
                                                font.pixelSize: 12
                                                font.weight: Font.Medium
                                            }
                                        }
                                        Text {
                                            Layout.fillWidth: true
                                            text: modelData.pci + "  ·  " + modelData.driver
                                            color: root.mutedInk
                                            font.pixelSize: 12
                                            elide: Text.ElideRight
                                        }
                                        Text {
                                            Layout.fillWidth: true
                                            visible: !modelData.loaded
                                            text: "The driver shipped in the image did not bind to this GPU."
                                            color: root.mutedInk
                                            font.pixelSize: 12
                                            elide: Text.ElideRight
                                        }
                                    }
                                }
                            }
                            Text {
                                Layout.fillWidth: true
                                visible: drivers.gpus.length === 0
                                text: "No GPU detected"
                                color: root.negativeColor
                                font.pixelSize: 14
                            }
                            Text {
                                Layout.fillWidth: true
                                visible: drivers.note !== ""
                                text: drivers.note
                                color: root.mutedInk
                                font.pixelSize: 13
                                wrapMode: Text.WordWrap
                            }
                            Item { Layout.fillHeight: true }
                        }

                        ColumnLayout {
                            spacing: 12
                            Text {
                                text: "Gaming tweaks"
                                color: root.ink
                                font.pixelSize: 22
                                font.weight: Font.DemiBold
                            }
                            Text {
                                Layout.fillWidth: true
                                text: "Optional tuning for games and the desktop."
                                color: root.mutedInk
                                font.pixelSize: 13
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                implicitHeight: 1
                                color: root.lineColor
                            }
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 16
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 3
                                    Text {
                                        text: "sched_ext gaming scheduler (scx_lavd)"
                                        color: root.ink
                                        font.pixelSize: 14
                                        font.weight: Font.DemiBold
                                    }
                                    Text {
                                        text: tweaks.scxEnabled ? "Enabled" : "Disabled"
                                        color: tweaks.scxEnabled ? root.positiveColor : root.mutedInk
                                        font.pixelSize: 12
                                    }
                                    Text {
                                        Layout.fillWidth: true
                                        visible: tweaks.scxAvailable
                                        text: "Runs scx_lavd through avenor-scx.service."
                                        color: root.mutedInk
                                        font.pixelSize: 12
                                        wrapMode: Text.WordWrap
                                    }
                                    Text {
                                        Layout.fillWidth: true
                                        visible: !tweaks.scxAvailable
                                        text: "Not available: /sys/kernel/sched_ext is missing."
                                        color: root.mutedInk
                                        font.pixelSize: 12
                                        wrapMode: Text.WordWrap
                                    }
                                }
                                Toggle {
                                    Layout.alignment: Qt.AlignVCenter
                                    value: tweaks.scxEnabled
                                    available: tweaks.scxAvailable && !tweaks.busy
                                    onToggled: function(state) { tweaks.setScx(state) }
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                implicitHeight: 1
                                color: root.lineColor
                            }
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 16
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 3
                                    Text {
                                        text: "MangoHud overlay in all Vulkan games"
                                        color: root.ink
                                        font.pixelSize: 14
                                        font.weight: Font.DemiBold
                                    }
                                    Text {
                                        text: tweaks.mangohudEnabled ? "Enabled" : "Disabled"
                                        color: tweaks.mangohudEnabled ? root.positiveColor : root.mutedInk
                                        font.pixelSize: 12
                                    }
                                    Text {
                                        Layout.fillWidth: true
                                        text: "Applies after the next login."
                                        color: root.mutedInk
                                        font.pixelSize: 12
                                        wrapMode: Text.WordWrap
                                    }
                                }
                                Toggle {
                                    Layout.alignment: Qt.AlignVCenter
                                    value: tweaks.mangohudEnabled
                                    available: !tweaks.busy
                                    onToggled: function(state) { tweaks.setMangohud(state) }
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                implicitHeight: 1
                                color: root.lineColor
                            }
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 16
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 3
                                    Text {
                                        Layout.fillWidth: true
                                        text: "GameMode daemon"
                                        color: root.ink
                                        font.pixelSize: 14
                                        font.weight: Font.DemiBold
                                    }
                                    Text {
                                        text: tweaks.gamemodeEnabled ? "Enabled" : "Disabled"
                                        color: tweaks.gamemodeEnabled ? root.positiveColor : root.mutedInk
                                        font.pixelSize: 12
                                    }
                                }
                                Toggle {
                                    Layout.alignment: Qt.AlignVCenter
                                    value: tweaks.gamemodeEnabled
                                    available: !tweaks.busy
                                    onToggled: function(state) { tweaks.setGamemode(state) }
                                }
                            }
                            Text {
                                Layout.fillWidth: true
                                text: "Always on: vm.max_map_count, low swappiness, THP madvise"
                                color: root.mutedInk
                                font.pixelSize: 12
                                wrapMode: Text.WordWrap
                            }
                            Text {
                                Layout.fillWidth: true
                                visible: tweaks.busy
                                text: "Applying..."
                                color: root.mutedInk
                                font.pixelSize: 12
                            }
                            Text {
                                Layout.fillWidth: true
                                visible: tweaks.error !== ""
                                text: tweaks.error
                                color: root.negativeColor
                                font.pixelSize: 12
                                wrapMode: Text.WordWrap
                            }
                            Item { Layout.fillHeight: true }
                        }

                        ColumnLayout {
                            spacing: 12
                            Text {
                                text: "FrameFX"
                                color: root.ink
                                font.pixelSize: 22
                                font.weight: Font.DemiBold
                            }
                            Text {
                                Layout.fillWidth: true
                                text: "Optional frame generation for Vulkan games."
                                color: root.mutedInk
                                font.pixelSize: 13
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                visible: framefx.isInstalled
                                implicitHeight: 54
                                radius: 8
                                color: "#f0f5f0"
                                border.width: 1
                                border.color: "#d9e5d9"
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 12
                                    Text {
                                        text: "Installed"
                                        color: root.positiveColor
                                        font.pixelSize: 14
                                        font.weight: Font.DemiBold
                                    }
                                    Item { Layout.fillWidth: true }
                                    Text {
                                        Layout.fillWidth: true
                                        text: "~/.local/share/framefx/Universal-FrameFX.AppImage"
                                        color: root.mutedInk
                                        font.pixelSize: 11
                                        elide: Text.ElideLeft
                                        horizontalAlignment: Text.AlignRight
                                    }
                                }
                            }
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                visible: framefx.tagName !== ""
                                Text {
                                    text: framefx.tagName
                                    color: root.ink
                                    font.pixelSize: 14
                                    font.weight: Font.DemiBold
                                }
                                Text {
                                    text: framefx.sizeLabel
                                    color: root.mutedInk
                                    font.pixelSize: 12
                                }
                            }
                            Text {
                                Layout.fillWidth: true
                                visible: framefx.status === "loading"
                                text: "Checking releases..."
                                color: root.mutedInk
                                font.pixelSize: 13
                            }
                            Text {
                                Layout.fillWidth: true
                                visible: framefx.status === "offline" || framefx.status === "error"
                                text: framefx.messageText
                                color: root.negativeColor
                                font.pixelSize: 13
                                wrapMode: Text.WordWrap
                            }
                            ActionButton {
                                visible: framefx.status === "ready"
                                text: "Install"
                                primary: true
                                onClicked: framefx.install()
                            }
                            ActionButton {
                                visible: framefx.status === "offline" || framefx.status === "error"
                                text: "Retry"
                                onClicked: framefx.load()
                            }
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 6
                                visible: framefx.status === "installing"
                                Text {
                                    text: "Installing..."
                                    color: root.ink
                                    font.pixelSize: 13
                                }
                                ProgressBar {
                                    Layout.fillWidth: true
                                    from: 0
                                    to: 1
                                    value: framefx.progressValue
                                }
                            }
                            Item { Layout.fillHeight: true }
                        }

                        ColumnLayout {
                            spacing: 16
                            Item { Layout.fillHeight: true }
                            Text {
                                Layout.fillWidth: true
                                text: "You're all set"
                                horizontalAlignment: Text.AlignHCenter
                                color: root.ink
                                font.pixelSize: 28
                                font.weight: Font.DemiBold
                            }
                            Text {
                                Layout.fillWidth: true
                                text: "AvenorOS is ready. You can close this window."
                                horizontalAlignment: Text.AlignHCenter
                                color: root.mutedInk
                                font.pixelSize: 14
                            }
                            CheckBox {
                                id: showAtStartup
                                Layout.alignment: Qt.AlignHCenter
                                text: "Show this at startup"
                                checked: app.showAgain
                                onToggled: app.setShowAgain(checked)
                                font.pixelSize: 14
                                contentItem: Text {
                                    leftPadding: showAtStartup.indicator.width + showAtStartup.spacing
                                    text: showAtStartup.text
                                    color: root.ink
                                    font: showAtStartup.font
                                    verticalAlignment: Text.AlignVCenter
                                }
                                indicator: Rectangle {
                                    implicitWidth: 18
                                    implicitHeight: 18
                                    x: showAtStartup.leftPadding
                                    y: parent.height / 2 - height / 2
                                    radius: 4
                                    color: showAtStartup.checked ? root.accentColor : "#ffffff"
                                    border.width: 1
                                    border.color: showAtStartup.checked ? root.accentColor : root.lineColor
                                    Text {
                                        anchors.centerIn: parent
                                        visible: showAtStartup.checked
                                        text: "\u2713"
                                        color: "#ffffff"
                                        font.pixelSize: 12
                                    }
                                }
                            }
                            Item { Layout.fillHeight: true }
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    Item { Layout.fillWidth: true }
                    ActionButton {
                        text: "Back"
                        enabled: app.currentPage > 0
                        onClicked: app.backPage()
                    }
                    ActionButton {
                        text: app.currentPage === 4 ? "Close" : "Next"
                        primary: true
                        onClicked: {
                            if (app.currentPage === 4) app.finish()
                            else app.nextPage()
                        }
                    }
                }
            }
        }
    }
}
