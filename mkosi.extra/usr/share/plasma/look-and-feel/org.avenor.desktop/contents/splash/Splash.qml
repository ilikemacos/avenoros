import QtQuick

Rectangle {
    id: root

    property int stage

    color: "#0b1220"

    onStageChanged: if (stage === 1) intro.start()

    Image {
        id: logo
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) * 0.42
        height: width
        source: "images/avenor.png"
        sourceSize.width: 640
        sourceSize.height: 640
        smooth: true
        opacity: 0
    }

    Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: logo.bottom
        anchors.topMargin: 24
        width: 120
        height: 3
        radius: 1.5
        color: Qt.rgba(1, 1, 1, 0.12)

        Rectangle {
            width: parent.width * Math.min(1, root.stage / 6)
            height: parent.height
            radius: parent.radius
            color: Qt.rgba(1, 1, 1, 0.7)
            Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
        }
    }

    OpacityAnimator {
        id: intro
        target: logo
        from: 0
        to: 1
        duration: 500
        easing.type: Easing.OutCubic
    }
}
