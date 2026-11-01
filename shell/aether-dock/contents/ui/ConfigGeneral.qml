import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Dialogs as Dialogs
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.plasma.configuration
import org.kde.plasma.plasmoid

Kirigami.FormLayout {
    property alias cfg_iconSize: iconSize.value
    property alias cfg_spacing: spacing.value
    property alias cfg_cornerRadius: cornerRadius.value
    property alias cfg_opacity: opacity.value
    property alias cfg_accentColor: accentColor.color
    property var cfg_launchers

    function launcherList(value) {
        const configured = value === undefined || value === null
            ? Plasmoid.configuration.launchers
            : value
        if (Array.isArray(configured)) {
            return configured.map(item => String(item).trim())
                .filter(item => item.length > 0)
        }
        if (typeof configured === "string") {
            return configured.split(/[,\n]/)
                .map(item => item.trim())
                .filter(item => item.length > 0)
        }
        if (configured !== undefined && configured !== null) {
            if (typeof configured.length === "number") {
                const items = []
                for (let index = 0; index < configured.length; index += 1) {
                    items.push(String(configured[index]).trim())
                }
                return items.filter(item => item.length > 0)
            }
            const serialized = String(configured)
            if (serialized !== "[object Object]") {
                return serialized.split(/[,\n]/)
                    .map(item => item.trim())
                    .filter(item => item.length > 0)
            }
        }
        return []
    }

    function launcherText(value) {
        return launcherList(value).join("\n")
    }

    Component.onCompleted: {
        if (launcherList(cfg_launchers).length === 0) {
            cfg_launchers = launcherList(Plasmoid.configuration.launchers)
        }
        launchers.text = launcherText(cfg_launchers)
    }

    QQC2.SpinBox {
        id: iconSize
        Kirigami.FormData.label: i18n("Icon size")
        from: 24
        to: 64
    }

    QQC2.SpinBox {
        id: spacing
        Kirigami.FormData.label: i18n("Spacing")
        from: 0
        to: 24
    }

    QQC2.SpinBox {
        id: cornerRadius
        Kirigami.FormData.label: i18n("Corner radius")
        from: 8
        to: 40
    }

    QQC2.Slider {
        id: opacity
        Kirigami.FormData.label: i18n("Dock opacity")
        from: 45
        to: 100
        stepSize: 1
        value: 92
    }

    QQC2.TextArea {
        id: launchers
        Kirigami.FormData.label: i18n("Pinned application IDs")
        placeholderText: i18n("One applications:*.desktop URL per line")
        text: launcherText(cfg_launchers)
        implicitHeight: 96
        onTextChanged: {
            const entries = text.split("\n")
                .map(item => item.trim())
                .filter(item => item.length > 0)
            if (entries.length === 0
                || entries.every(item => /^applications:.+\.desktop$/.test(item))) {
                cfg_launchers = entries
            }
        }
    }

    QQC2.Button {
        id: accentColor
        property color color: "#54D6FF"
        Kirigami.FormData.label: i18n("Accent")
        text: color.toString()
        onClicked: colorDialog.open()
    }

    Dialogs.ColorDialog {
        id: colorDialog
        selectedColor: accentColor.color
        onAccepted: accentColor.color = selectedColor
    }
}
