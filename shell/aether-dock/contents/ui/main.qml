import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.plasma.plasmoid
import org.kde.taskmanager as TaskManager

PlasmoidItem {
    id: dock

    preferredRepresentation: fullRepresentation

    readonly property int iconSize: Plasmoid.configuration.iconSize
    readonly property int itemWidth: iconSize + 12
    readonly property int taskRowWidth: tasksModel.count * itemWidth
        + Math.max(0, tasksModel.count - 1) * Plasmoid.configuration.spacing

    implicitWidth: Math.max(64, taskRowWidth + 12)
    implicitHeight: iconSize + 12

    Layout.preferredWidth: implicitWidth
    Layout.preferredHeight: implicitHeight

    TaskManager.VirtualDesktopInfo {
        id: virtualDesktopInfo
    }

    TaskManager.TasksModel {
        id: tasksModel
        virtualDesktop: virtualDesktopInfo.currentDesktop
        screenGeometry: Plasmoid.containment.screenGeometry
        filterByVirtualDesktop: true
        filterByScreen: false
        filterByActivity: false
        filterNotMinimized: false
        separateLaunchers: false
        sortMode: TaskManager.TasksModel.SortManual
        groupMode: TaskManager.TasksModel.GroupApplications
        launcherList: Plasmoid.configuration.launchers

        onLauncherListChanged: {
            if (JSON.stringify(launcherList) !== JSON.stringify(Plasmoid.configuration.launchers)) {
                Plasmoid.configuration.launchers = launcherList
            }
        }
    }

    fullRepresentation: Item {
        id: representation
        implicitWidth: dock.implicitWidth
        implicitHeight: dock.implicitHeight

        Row {
            id: taskRow
            anchors.centerIn: parent
            spacing: Plasmoid.configuration.spacing
            width: dock.taskRowWidth
            height: parent.height

            Repeater {
                model: tasksModel

                delegate: Item {
                    id: taskItem
                    required property int index
                    required property var model

                    width: dock.itemWidth
                    height: representation.height

                    Rectangle {
                        anchors.centerIn: parent
                        width: Math.min(parent.width - 2, dock.iconSize + 10)
                        height: Math.min(parent.height - 2, dock.iconSize + 10)
                        radius: Math.min(Plasmoid.configuration.cornerRadius, height / 2)
                        color: Plasmoid.configuration.accentColor
                        opacity: taskItem.model.IsActive
                            ? (Plasmoid.configuration.opacity / 100) * 0.30
                            : (mouseArea.containsMouse ? 0.12 : 0)
                        Behavior on opacity {
                            NumberAnimation {
                                duration: 120
                                easing.type: Easing.OutCubic
                            }
                        }
                    }

                    Kirigami.Icon {
                        anchors.centerIn: parent
                        width: dock.iconSize
                        height: dock.iconSize
                        source: taskItem.model.decoration
                        scale: mouseArea.pressed ? 0.92 : 1.0
                        Behavior on scale {
                            NumberAnimation {
                                duration: 90
                                easing.type: Easing.OutCubic
                            }
                        }
                    }

                    Rectangle {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: 2
                        width: taskItem.model.IsActive ? 16 : 5
                        height: 3
                        radius: 1.5
                        color: Plasmoid.configuration.accentColor
                        visible: taskItem.model.IsWindow
                        Behavior on width {
                            NumberAnimation {
                                duration: 140
                                easing.type: Easing.OutCubic
                            }
                        }
                    }

                    MouseArea {
                        id: mouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        acceptedButtons: Qt.LeftButton | Qt.MiddleButton

                        onClicked: mouse => {
                            const taskIndex = tasksModel.makeModelIndex(taskItem.index)
                            if (mouse.button === Qt.MiddleButton) {
                                tasksModel.requestClose(taskIndex)
                            } else if (taskItem.model.IsMinimized) {
                                tasksModel.requestToggleMinimized(taskIndex)
                                tasksModel.requestActivate(taskIndex)
                            } else if (taskItem.model.IsActive && taskItem.model.IsWindow) {
                                tasksModel.requestToggleMinimized(taskIndex)
                            } else {
                                tasksModel.requestActivate(taskIndex)
                            }
                        }
                    }
                }
            }
        }
    }
}
