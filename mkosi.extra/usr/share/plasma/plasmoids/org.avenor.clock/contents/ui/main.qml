import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    property date now: new Date()

    preferredRepresentation: fullRepresentation
    toolTipMainText: Qt.formatDate(now, Qt.TextDate)

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: root.now = new Date()
    }

    fullRepresentation: Text {
        Layout.minimumWidth: contentWidth + Kirigami.Units.largeSpacing * 2
        Layout.fillHeight: true
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        text: Qt.formatDateTime(root.now, "ddd h:mm AP")
        color: Kirigami.Theme.textColor
        font.pixelSize: 13
        font.weight: Font.Medium
        font.features: { "tnum": 1 }
    }
}
