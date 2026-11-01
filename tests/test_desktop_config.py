import json
import runpy
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_LIST = ROOT / "build" / "config" / "package-lists" / "aether.list.chroot"
SESSION_CONFIG = (
    ROOT
    / "build"
    / "config"
    / "includes.chroot"
    / "etc"
    / "lightdm"
    / "lightdm.conf.d"
    / "50-aether-session.conf"
)
PLASMA_PANEL_DEFAULT = (
    ROOT
    / "build"
    / "config"
    / "includes.chroot"
    / "etc"
    / "skel"
    / ".config"
    / "plasma-org.kde.plasma.desktop-appletsrc"
)
PANEL_SEED_SCRIPT = (
    ROOT
    / "build"
    / "config"
    / "includes.chroot"
    / "usr"
    / "local"
    / "sbin"
    / "aether-seed-plasma-panel"
)
DOCK_SOURCE = ROOT / "shell" / "aether-dock"
WELCOME_APP = (
    ROOT
    / "build"
    / "config"
    / "includes.chroot"
    / "usr"
    / "bin"
    / "aether-welcome"
)


class DesktopConfigTests(unittest.TestCase):
    def setUp(self):
        self.packages = {
            line.strip()
            for line in PACKAGE_LIST.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }

    def test_kde_plasma_desktop_and_display_manager_are_installed(self):
        self.assertTrue(
            {
                "plasma-desktop",
                "plasma-workspace",
                "kwin-x11",
                "xserver-xorg",
                "lightdm",
                "dolphin",
                "konsole",
            }
            <= self.packages
        )

    def test_lightdm_has_a_graphical_greeter(self):
        self.assertIn("lightdm-gtk-greeter", self.packages)
        greeter = (
            ROOT
            / "build"
            / "config"
            / "includes.chroot"
            / "etc"
            / "lightdm"
            / "lightdm-gtk-greeter.conf"
        ).read_text(encoding="utf-8")
        self.assertIn("theme-name = Adwaita-dark", greeter)
        self.assertIn("background = /usr/share/wallpapers/Aether", greeter)
        self.assertIn("clock-format = %H:%M", greeter)

    def test_lightdm_starts_the_kde_x11_session(self):
        config = SESSION_CONFIG.read_text(encoding="utf-8")
        self.assertIn("[Seat:*]", config)
        self.assertIn("user-session=plasmax11", config)
        self.assertIn(
            "session-setup-script=/usr/local/sbin/aether-seed-plasma-panel", config
        )

    def test_live_session_seeds_the_aether_panel_once(self):
        script = PANEL_SEED_SCRIPT.read_text(encoding="utf-8")
        build_script = (ROOT / "scripts" / "build-live-iso.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("plasma-org.kde.plasma.desktop-appletsrc", script)
        self.assertIn(".aether-panel-seeded", script)
        self.assertIn('chmod 0755 "${AETHER_PANEL_SEED_SCRIPT}"', build_script)
        self.assertIn("kdeglobals", script)
        self.assertIn("plasma-welcomerc", script)
        self.assertIn("seed_file", script)

    def test_build_uses_temporary_ipv4_preference_for_package_downloads(self):
        build_script = (ROOT / "scripts" / "build-live-iso.sh").read_text(
            encoding="utf-8"
        )
        wget_config = (ROOT / "build" / "aether-build-wgetrc").read_text(
            encoding="utf-8"
        )
        cleanup_hook_path = (
            ROOT
            / "build"
            / "config"
            / "hooks"
            / "normal"
            / "9990-remove-aether-build-wgetrc.hook.chroot"
        )
        cleanup_hook = cleanup_hook_path.read_text(encoding="utf-8")
        self.assertNotIn(b"\r", cleanup_hook_path.read_bytes())
        self.assertIn("prefer-family = IPv4", wget_config)
        self.assertIn('WGETRC="${AETHER_WGETRC_HOST}" lb build', build_script)
        self.assertIn("includes.chroot_before_packages/root/.wgetrc", build_script)
        self.assertIn("rm -f /root/.wgetrc", cleanup_hook)
        self.assertLess(
            build_script.index('sed -i "s|@AETHER_WGETRC_PATH@|'),
            build_script.index("sed -i 's/\\r$//' \"${AETHER_WGETRC_HOOK}\""),
        )

    def test_plasma_welcome_is_disabled_for_live_sessions(self):
        welcome = (
            ROOT
            / "build"
            / "config"
            / "includes.chroot"
            / "etc"
            / "skel"
            / ".config"
            / "plasma-welcomerc"
        ).read_text(encoding="utf-8")
        autostart = (
            ROOT
            / "build"
            / "config"
            / "includes.chroot"
            / "etc"
            / "xdg"
            / "autostart"
            / "org.kde.plasma-welcome.desktop"
        ).read_text(encoding="utf-8")
        hook = (
            ROOT
            / "build"
            / "config"
            / "hooks"
            / "live"
            / "0100-disable-plasma-welcome.hook.chroot"
        ).read_text(encoding="utf-8")
        self.assertIn("LastVersion=99.99.99", welcome)
        self.assertIn("Hidden=true", autostart)
        self.assertIn("org.kde.plasma-welcome.desktop", hook)
        self.assertIn("Hidden=true", hook)

    def test_aether_welcome_is_packaged_and_autostarts_only_on_first_run(self):
        self.assertTrue({"python3-gi", "gir1.2-gtk-3.0"} <= self.packages)
        app = runpy.run_path(str(WELCOME_APP))
        build_script = (ROOT / "scripts" / "build-live-iso.sh").read_text(
            encoding="utf-8"
        )
        autostart = (
            ROOT
            / "build"
            / "config"
            / "includes.chroot"
            / "etc"
            / "xdg"
            / "autostart"
            / "aether-welcome.desktop"
        ).read_text(encoding="utf-8")
        launcher = (
            ROOT
            / "build"
            / "config"
            / "includes.chroot"
            / "usr"
            / "share"
            / "applications"
            / "aether-welcome.desktop"
        ).read_text(encoding="utf-8")
        self.assertIn("Exec=/usr/bin/aether-welcome --first-run", autostart)
        self.assertIn("Exec=/usr/bin/aether-welcome", launcher)
        self.assertIn('sed -i \'s/\\r$//\' "${AETHER_WELCOME_APP}"', build_script)

    def test_aether_welcome_first_run_skips_live_and_completed_sessions(self):
        app = runpy.run_path(str(WELCOME_APP))
        should_show = app["should_show_first_run"]
        with tempfile.TemporaryDirectory() as directory:
            completion_file = Path(directory) / "completed"
            live_marker = Path(directory) / "live"
            self.assertTrue(should_show(completion_file, live_marker))
            live_marker.touch()
            self.assertFalse(should_show(completion_file, live_marker))
            live_marker.unlink()
            app["mark_completed"](completion_file)
            self.assertFalse(should_show(completion_file, live_marker))

    def test_graphical_vt_service_is_enabled_by_the_build_script(self):
        build_script = (ROOT / "scripts" / "build-live-iso.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("graphical.target.wants", build_script)
        self.assertIn(
            "ln -sfn ../aether-activate-graphical-vt.service", build_script
        )
        # The repository must not carry platform-specific symlinks; the build
        # creates them so a checkout works on Windows and Linux alike.
        wants = (
            ROOT
            / "build"
            / "config"
            / "includes.chroot"
            / "etc"
            / "systemd"
            / "system"
            / "graphical.target.wants"
        )
        self.assertFalse(wants.exists())


    def test_default_plasma_panel_includes_the_aether_dock(self):
        config = PLASMA_PANEL_DEFAULT.read_text(encoding="utf-8")
        self.assertIn("plugin=org.aether.shell.dock", config)
        self.assertIn("plugin=org.kde.plasma.systemtray", config)
        self.assertIn("plugin=org.kde.plasma.digitalclock", config)
        self.assertIn("AppletOrder=3;7;4;8;5;6;", config)
        self.assertEqual(config.count("plugin=org.kde.plasma.panelspacer"), 2)
        self.assertIn(
            "launchers=applications:org.kde.dolphin.desktop,"
            "applications:org.kde.konsole.desktop,applications:systemsettings.desktop",
            config,
        )
        self.assertEqual(config.count("expanding=true"), 2)
        self.assertIn("alignment=132", config)
        self.assertIn("floating=1", config)
        self.assertIn("length=80", config)
        self.assertIn("file:///usr/share/wallpapers/Aether/contents/images/2560x1600.png", config)

    def test_aether_wallpaper_and_dark_scheme_are_seeded(self):
        build_script = (ROOT / "scripts" / "build-live-iso.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn('AETHER_WALLPAPER_SOURCE="${BUILD_DIR}/../wallpapers/default_wallpaper.png"', build_script)
        self.assertIn('${AETHER_WALLPAPER_TARGET}/2560x1600.png', build_script)
        kdeglobals = (
            ROOT
            / "build"
            / "config"
            / "includes.chroot"
            / "etc"
            / "skel"
            / ".config"
            / "kdeglobals"
        ).read_text(encoding="utf-8")
        self.assertIn("ColorScheme=BreezeDark", kdeglobals)
        self.assertIn("AccentColor=84,214,255", kdeglobals)
        self.assertIn("Theme=Aether", kdeglobals)
        icon_theme = (
            ROOT
            / "build"
            / "config"
            / "includes.chroot"
            / "usr"
            / "share"
            / "icons"
            / "Aether"
            / "index.theme"
        ).read_text(encoding="utf-8")
        self.assertIn("Inherits=breeze-dark,breeze,hicolor", icon_theme)
        desktop_config = (
            ROOT
            / "build"
            / "config"
            / "includes.chroot"
            / "etc"
            / "skel"
            / ".config"
            / "plasma-org.kde.plasma.desktop-appletsrc"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "Image=file:///usr/share/wallpapers/Aether/contents/images/2560x1600.png",
            desktop_config,
        )
        greeter = (
            ROOT
            / "build"
            / "config"
            / "includes.chroot"
            / "etc"
            / "lightdm"
            / "lightdm-gtk-greeter.conf"
        ).read_text(encoding="utf-8")
        self.assertIn("icon-theme-name = Aether", greeter)
        wallpaper_script = (
            ROOT
            / "build"
            / "config"
            / "includes.chroot"
            / "usr"
            / "local"
            / "bin"
            / "aether-set-default-wallpaper"
        ).read_text(encoding="utf-8")
        wallpaper_autostart = (
            ROOT
            / "build"
            / "config"
            / "includes.chroot"
            / "etc"
            / "xdg"
            / "autostart"
            / "aether-default-wallpaper.desktop"
        ).read_text(encoding="utf-8")
        self.assertIn("plasma-apply-wallpaperimage", wallpaper_script)
        self.assertIn(".aether-default-wallpaper-set", wallpaper_script)
        self.assertIn("aether-set-default-wallpaper", wallpaper_autostart)
        self.assertIn('chmod 0755 "${AETHER_WALLPAPER_SCRIPT}"', build_script)
        for icon in (
            "dolphin.svg",
            "org.kde.dolphin.svg",
            "systemsettings.svg",
            "preferences-system.svg",
            "start-here.svg",
            "utilities-terminal.svg",
        ):
            self.assertTrue(
                (
                    ROOT
                    / "build"
                    / "config"
                    / "includes.chroot"
                    / "usr"
                    / "share"
                    / "icons"
                    / "Aether"
                    / "scalable"
                    / "apps"
                    / icon
                ).is_file()
            )

    def test_old_sway_greeter_stack_is_not_installed_as_the_login_path(self):
        self.assertTrue(
            {"greetd", "gtkgreet", "sway", "xfce4", "xfce4-goodies"}.isdisjoint(
                self.packages
            )
        )

    def test_aether_dock_is_installed_by_the_build_script(self):
        script = (ROOT / "scripts" / "build-live-iso.sh").read_text(encoding="utf-8")
        self.assertIn('AETHER_DOCK_SOURCE="${BUILD_DIR}/../shell/aether-dock"', script)
        self.assertIn("cp -a", script)
        self.assertTrue((DOCK_SOURCE / "metadata.json").is_file())

    def test_aether_dock_metadata_identifies_a_plasma_6_applet(self):
        metadata = json.loads((DOCK_SOURCE / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["KPackageStructure"], "Plasma/Applet")
        self.assertEqual(metadata["KPlugin"]["Id"], "org.aether.shell.dock")
        self.assertEqual(metadata["X-Plasma-API-Minimum-Version"], "6.0")

    def test_aether_dock_uses_real_window_tasks_and_configurable_launchers(self):
        qml = (DOCK_SOURCE / "contents" / "ui" / "main.qml").read_text(encoding="utf-8")
        config = (
            DOCK_SOURCE / "contents" / "config" / "main.xml"
        ).read_text(encoding="utf-8")
        self.assertIn("import org.kde.kirigami as Kirigami", qml)
        self.assertIn("Kirigami.Icon", qml)
        self.assertNotIn("PlasmaCore.IconItem", qml)
        root_item = qml.split("fullRepresentation: Item", 1)[0]
        self.assertIn("tasksModel.count", root_item)
        self.assertIn("readonly property int taskRowWidth", root_item)
        self.assertIn("width: dock.taskRowWidth", qml)
        self.assertNotIn("implicitWidth: width", qml)
        self.assertIn("TaskManager.TasksModel", qml)
        self.assertIn("separateLaunchers: false", qml)
        self.assertIn("requestActivate", qml)
        self.assertIn("requestToggleMinimized", qml)
        for key in ("launchers", "iconSize", "spacing", "cornerRadius", "opacity"):
            self.assertIn(f'name="{key}"', config)
        config_ui = (DOCK_SOURCE / "contents" / "ui" / "ConfigGeneral.qml").read_text(
            encoding="utf-8"
        )
        self.assertIn("ColorDialog", config_ui)
        self.assertIn("Plasmoid.configuration.launchers", config_ui)
        self.assertIn('typeof configured.length === "number"', config_ui)
        self.assertIn("String(configured)", config_ui)
        self.assertIn("launchers.text = launcherText(cfg_launchers)", config_ui)
        self.assertIn("entries.every(item => /^applications:.+\\.desktop$/.test(item))", config_ui)
        self.assertIn("implicitHeight: 96", config_ui)


if __name__ == "__main__":
    unittest.main()
