import QtQuick
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasma5support as P5Support

PlasmoidItem {
    id: root

    readonly property var battery: source.data["Battery"] ?? {}
    readonly property bool present: battery["Has Battery"] ?? false
    readonly property int percent: battery["Percent"] ?? 0
    readonly property bool charging: battery["State"] === "Charging"

    preferredRepresentation: fullRepresentation
    Plasmoid.status: present ? PlasmaCore.Types.ActiveStatus : PlasmaCore.Types.HiddenStatus
    toolTipMainText: present ? percent + "%" : ""
    toolTipSubText: charging ? "Charging" : ""

    P5Support.DataSource {
        id: source
        engine: "powermanagement"
        connectedSources: ["Battery"]
        interval: 30000
    }

    fullRepresentation: Item {
        implicitWidth: pill.width + nub.width + 2
        implicitHeight: pill.height

        Rectangle {
            id: pill
            anchors.verticalCenter: parent.verticalCenter
            width: Math.round(height * 2.1)
            height: 20
            radius: height / 2
            color: "#ffffff"
            border.color: Qt.rgba(0, 0, 0, 0.12)
            border.width: 1

            Text {
                anchors.centerIn: parent
                text: root.percent
                color: root.percent <= 10 && !root.charging ? "#c2410c" : "#1f1d1a"
                font.pixelSize: 12
                font.weight: Font.DemiBold
                font.features: { "tnum": 1 }
            }
        }

        Rectangle {
            id: nub
            anchors.left: pill.right
            anchors.leftMargin: 2
            anchors.verticalCenter: pill.verticalCenter
            width: 3
            height: 7
            radius: 1.5
            color: "#ffffff"
            opacity: 0.85
        }
    }
}
