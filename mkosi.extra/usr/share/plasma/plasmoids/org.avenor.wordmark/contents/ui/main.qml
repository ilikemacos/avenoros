import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.plasma5support as P5Support
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    preferredRepresentation: fullRepresentation
    toolTipMainText: "Search"

    P5Support.DataSource {
        id: shell
        engine: "executable"
        onNewData: sourceName => disconnectSource(sourceName)
    }

    fullRepresentation: MouseArea {
        Layout.minimumWidth: row.implicitWidth + Kirigami.Units.largeSpacing * 2
        Layout.fillHeight: true
        hoverEnabled: true
        onClicked: shell.connectSource("krunner")

        Row {
            id: row
            anchors.centerIn: parent
            spacing: 6

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: "Avenor"
                color: Kirigami.Theme.textColor
                opacity: parent.parent.containsMouse ? 0.7 : 1
                font.pixelSize: 16
                font.weight: Font.Medium
            }

            Rectangle {
                anchors.verticalCenter: parent.verticalCenter
                width: 6
                height: 6
                radius: 3
                color: Kirigami.Theme.disabledTextColor
            }
        }
    }
}
