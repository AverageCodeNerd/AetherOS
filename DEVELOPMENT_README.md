# AetherOS

## An experimental Debian-based Linux desktop

**AetherOS** is an in-development Linux distribution built on Debian 13. Its goal is a distinctive, customizable desktop with a futuristic visual style, backed by Debian's established system and package infrastructure.

The current prototype combines KDE Plasma with Aether desktop components, including a custom dock, Aether wallpaper and icons, and a GTK Welcome guide. The project is working toward an original desktop shell rather than treating a themed stock desktop as the finished product.

## Current status

The hybrid live image and Debian installer have been exercised in disposable QEMU VMs in BIOS and UEFI configurations. The customized desktop, dock interactions, and BIOS/UEFI installation paths have been tested there. The Aether Welcome guide has rendered in a UEFI live session.

**This is an experimental development build, not a beta release.** KDE's generic Welcome Center still opens at startup in the latest Welcome test image, and the installed first-run Welcome flow and completion persistence have not yet been verified. Real-hardware compatibility and broader hardware coverage also remain untested.

## Plans

1. Resolve the competing KDE Welcome startup and verify Aether Welcome on an installed system, including repeat-login behavior.
2. Continue building Aether Shell features and customization beyond the current dock and Plasma integration.
3. Develop first-party applications, including Aether Store and Aether Settings, and a coherent theme and wallpaper system.
4. Expand installation, update, accessibility, and hardware testing; publish a beta only after the remaining acceptance checks are met.

For build details and safe VM testing, see [docs/BUILD.md](docs/BUILD.md) and [docs/VM_TESTING.md](docs/VM_TESTING.md). No ISO download is published yet; the generated ISO is intentionally kept out of Git.

---

## Project vision

The long-term goal is to turn this concept into a real operating system that can be built, installed, booted, used daily, customized extensively, and maintained over time.

---

# 1. CORE VISION

Create a desktop operating system that feels like a plausible next-generation Windows release, while using the Linux ecosystem underneath.

The result must be:

- Visually exceptional, futuristic, cohesive, and professionally designed.
- Extremely customizable, with detailed controls over practically every aspect of the desktop.
- Stable enough for daily use, based on the latest official Debian Stable release available when development begins.
- Functional, with real applications, settings, file management, networking, updates, and software installation.
- Lightweight and responsive, avoiding unnecessary background services and excessive resource consumption.
- Free to build and use, preferring open-source software and avoiding subscriptions, proprietary dependencies, and unnecessary paid services.
- Distinctive enough to have its own identity rather than resembling an ordinary Linux distribution with a different wallpaper.

The aesthetic should combine futuristic Windows concept art, sophisticated dark interfaces, subtle glass effects, clean geometry, carefully controlled lighting, fluid motion, and excellent typography.

Use deep navy and near-black surfaces with ice-blue accents as the initial visual direction. Build a comprehensive theme system so users can completely change this identity later.

Avoid excessive neon, giant rounded rectangles everywhere, generic gradients, meaningless glowing borders, excessive blur, and decorative effects that compromise readability or performance.

**Quality requirement:** Every interface must look deliberately designed. No unfinished placeholder screens, random icon sets, inconsistent spacing, default-looking utility windows, fake buttons, nonfunctional settings, or generic AI-generated dashboard layouts.

---

# 2. OPERATING SYSTEM FOUNDATION

Use the latest officially released Debian Stable version available at the time the project begins.

Before implementation:

1. Research the current Debian Stable release through official Debian sources.
2. Identify the appropriate architecture, installation media, package repositories, bootloader, filesystem options, and supported hardware.
3. Determine the most reliable way to build a reproducible, bootable distribution.
4. Document the chosen architecture and its trade-offs.
5. Start implementing immediately after establishing a reasonable architecture. Do not spend the entire project researching.

Use the official Linux kernel sources and Debian's established infrastructure wherever appropriate.

Acquire the kernel and all required build components automatically. Prefer Debian's supported kernel packages for the initial stable system, and build a custom kernel only if a concrete project requirement justifies it.

Use Debian's package management, security updates, hardware support, and system utilities rather than reinventing mature infrastructure.

The distribution should include:

- A bootable UEFI installation.
- A suitable bootloader.
- A reliable root filesystem.
- A functioning display stack.
- Hardware detection and driver integration.
- Networking and Wi-Fi support.
- Audio support.
- Bluetooth support where hardware is available.
- Storage management and removable-device support.
- A graphical login screen.
- A first-boot setup experience.
- A complete desktop environment.
- An installer that can install the operating system onto a real computer or virtual machine.
- Recovery and troubleshooting facilities.

Prefer a Wayland-first desktop architecture.

Do not base the entire project on KDE Plasma, GNOME's default desktop experience, or a conventional desktop environment with superficial modifications. Build an original desktop shell around proven Linux components.

Do not reinvent the kernel, package manager, bootloader, or low-level hardware infrastructure without a compelling technical reason.

---

# 3. THE AETHER DESKTOP SHELL

Build an original desktop experience called **Aether Shell**.

The shell should be a coherent system rather than an unrelated collection of panels and widgets.

Choose a maintainable implementation architecture. Consider Rust for performance-critical services and shell components, and GTK4, Qt, or another appropriate native UI framework for graphical applications. Select the technology based on actual requirements, available libraries, maintainability, and integration with Wayland.

Avoid unnecessary dependencies and avoid building an entire compositor from scratch unless absolutely necessary.

The desktop must include the following functional components.

## 3.1 Desktop and workspace

Implement:

- A clean desktop canvas with configurable icons and shortcuts.
- Multiple virtual workspaces.
- Configurable window management.
- Window snapping and tiling.
- Drag-and-drop window placement.
- Keyboard shortcuts.
- A task switcher.
- An application launcher.
- A global search interface.
- A notification center.
- Quick settings.
- System status indicators.
- A clipboard history manager.
- A customizable lock screen.
- A screen capture utility.
- Multi-monitor support with independent display configuration.
- Fractional scaling support where the underlying stack supports it.
- A polished first-login experience.

Provide a conventional windowed workflow as well as optional advanced tiling workflows.

Do not force users to use a tiling window manager.

## 3.2 Taskbar

Create a distinctive, floating, centered taskbar inspired by the Windows 12 concept.

Support:

- Centered, left-aligned, and edge-aligned layouts.
- Floating and docked modes.
- Configurable height, width, spacing, transparency, blur, and corner radius.
- Pinned applications.
- Running-application indicators.
- Window previews where technically feasible.
- Application grouping.
- System tray icons.
- Clock and calendar.
- Network, sound, battery, and other applicable status indicators.
- Configurable animation styles.
- Per-monitor taskbars.
- Optional secondary panels.
- A compact mode.
- An advanced customization mode.

The taskbar must be a real interactive application launcher and window-management surface, not a static imitation.

## 3.3 Application launcher and search

Create a polished launcher with:

- Installed applications.
- Search as the user types.
- Application categories.
- Recent applications and files, with privacy controls.
- Pinned applications.
- Configurable layouts.
- Keyboard navigation.
- Search providers for applications, files, settings, and available software.
- Optional command execution, with safe handling of shell commands.
- A clear separation between normal searches and potentially dangerous administrative commands.

The launcher should feel instantaneous and remain usable on modest hardware.

## 3.4 Notification center and quick settings

Build a unified interface for notifications and system controls.

Provide real controls for available functionality, including:

- Wi-Fi.
- Bluetooth.
- Audio output and volume.
- Microphone mute.
- Display brightness.
- Night-light settings.
- Power profiles.
- Battery information.
- Screen recording or capture.
- Do Not Disturb.
- Media playback.
- VPN status where supported.

Only show controls that can actually work on the installed hardware and software stack.

## 3.5 File manager

Create a custom file manager called **Aether Files**.

It must support:

- Navigation through the filesystem.
- Multiple tabs.
- Split-pane browsing.
- Search.
- Sorting and filtering.
- Hidden files.
- File previews where supported.
- Archive browsing and extraction.
- Copy, move, rename, and delete operations.
- Drag and drop.
- Removable storage.
- Network locations where supported.
- Bookmarks and recent locations.
- File permissions and ownership information.
- A usable file properties dialog.
- Customizable icons, density, colors, and view modes.
- Dark and light themes.
- Keyboard shortcuts.

Use safe filesystem APIs, provide meaningful errors, and request elevated permissions only when necessary.

Do not run the file manager as root to bypass permission problems.

## 3.6 Window manager and effects

Integrate a reliable Wayland compositor that supports the selected architecture.

Implement or configure:

- Smooth window opening and closing.
- Workspace transitions.
- Focus animations.
- Window snapping.
- Tiling layouts.
- Rounded corners where supported.
- Transparency and blur where supported.
- Configurable shadows.
- Reduced-motion mode.
- Animation intensity and duration controls.
- Per-monitor behavior.
- A fallback configuration with visual effects disabled.

Animations should be fluid, subtle, and interruptible. Avoid excessive motion or animation delays that make the desktop feel slow.

Never sacrifice stability or responsiveness for visual effects.

---

# 4. EXTREME CUSTOMIZATION

Customization is one of the most important features of AETHER OS.

Build a dedicated **Aether Studio** application that allows users to customize the operating system through a polished graphical interface.

Do not require users to edit configuration files manually to access normal customization options.

## 4.1 Theme engine

Create a centralized theme system supporting:

- Dark, light, and custom themes.
- Global accent colors.
- Background colors.
- Surface colors.
- Text colors.
- Borders and separators.
- Window decorations.
- Corner radii.
- Transparency.
- Blur intensity.
- Shadows.
- Typography.
- Icon themes.
- Cursor themes.
- Animation profiles.
- Taskbar styling.
- Launcher styling.
- Notification styling.
- File manager styling.
- Login and lock screen styling where supported.
- Widget styling.
- Application-specific theme integration where feasible.

Changes should propagate across supported Aether applications consistently.

Provide a live preview and a reliable reset option.

## 4.2 Desktop layouts

Allow users to choose and modify desktop layouts.

Include several original presets:

- **Aether Horizon:** the primary futuristic Windows-inspired experience.
- **Aether Minimal:** clean, understated, and distraction-free.
- **Aether Terminal:** a keyboard-oriented developer environment.
- **Aether Studio:** a workspace designed for creative applications.
- **Aether Classic:** a more conventional desktop layout.
- **Aether Custom:** a completely user-defined layout.

Presets must be functional configurations rather than screenshots or superficial color changes.

Users must be able to modify a preset and save it as their own.

## 4.3 Customization controls

Expose settings for:

- Taskbar placement and dimensions.
- Panel layouts.
- Workspace behavior.
- Window tiling.
- Window animations.
- Desktop icons.
- Widget placement.
- System fonts.
- Icon sizes.
- Display scaling.
- Application launcher layout.
- Keyboard shortcuts.
- Mouse and touchpad behavior.
- Focus behavior.
- Window rules.
- Desktop spacing.
- Notification behavior.
- Lock screen appearance.
- Power-management preferences.

Advanced options should be organized into expandable sections so ordinary users are not overwhelmed.

## 4.4 Importing and sharing themes

Support exporting, importing, and sharing theme packages.

Create a documented theme format with versioning and validation.

Validate imported themes before applying them. Do not permit a theme package to execute arbitrary code simply because it contains visual assets.

Allow users to back up their complete desktop configuration and restore it later.

Provide a way to revert to a known-good configuration if a customization breaks the desktop.

---

# 5. WALLPAPER AND VISUAL ASSET SYSTEM

AETHER OS must not ship with only one wallpaper or rely on the default Debian backgrounds.

Create an original wallpaper collection with multiple distinct styles.

Include:

- Futuristic abstract landscapes.
- Minimal geometric designs.
- Dark architectural compositions.
- Atmospheric science-fiction environments.
- Ice-blue and deep-navy compositions.
- Green-accented alternatives.
- Minimal monochrome backgrounds.
- High-quality light-mode backgrounds.
- Subtle desktop textures.
- Multi-monitor compositions.

Obtain assets through legitimate sources, or generate original artwork where appropriate. Track licenses and attribution requirements.

Do not download copyrighted Windows wallpapers and redistribute them as original work.

Implement a wallpaper manager with:

- Multiple bundled wallpapers.
- Thumbnail previews.
- Search and categories.
- Favorites.
- Per-monitor wallpaper selection.
- Fit, fill, stretch, and center options.
- Solid-color backgrounds.
- Slideshow mode.
- Configurable transitions.
- Local wallpaper imports.
- Optional online wallpaper discovery.
- Optional live wallpapers, disabled by default if they significantly increase resource usage.

Wallpaper selection must integrate with the central theme system.

---

# 6. AETHER STORE — THE SOFTWARE CENTER

Create a full graphical application manager called **Aether Store**.

This is a core operating system application, not an optional mockup.

Its interface must look like a polished modern software marketplace, with useful information density, excellent search, and clear installation status.

## 6.1 Software discovery

Implement:

- Application search.
- Categories.
- Featured applications.
- Recently updated applications.
- Popular applications where trustworthy metadata is available.
- Application screenshots.
- Application icons.
- Descriptions.
- Version information.
- Developer or publisher information.
- License information.
- Supported architectures.
- Download size and estimated installed size where available.
- Dependency information where practical.
- Installation status.
- Update availability.
- Source repository information.
- Links to official websites and documentation.
- Changelogs where available.
- Uninstall and update controls.

Never fabricate ratings, download counts, screenshots, reviews, publisher identities, or other metadata.

If a data source does not provide a field, clearly indicate that it is unavailable.

## 6.2 Software sources

Integrate the following software sources where appropriate:

1. Debian's official APT repositories.
2. Debian package metadata.
3. Flatpak applications through properly configured repositories such as Flathub.
4. Locally installed Debian packages.
5. Additional repositories explicitly configured and approved by the user.

Make the origin of each application visible.

Clearly distinguish official Debian packages, Flatpak applications, third-party repositories, and local packages.

Do not silently add untrusted repositories or disable package-signature verification.

## 6.3 Installing and removing software

Users must be able to:

- Install applications.
- Cancel installations when safe.
- View installation progress.
- See meaningful error messages.
- Uninstall applications.
- View dependencies.
- View installed versions.
- Inspect application details.
- Open official documentation.
- Identify the package source.
- View installation history.
- Retry failed operations.

Use established package-management interfaces and supported system services rather than fragile shell-command parsing.

APT operations requiring elevated permissions must use a properly designed privileged backend or supported system service.

Do not run the graphical application store as root.

Avoid concurrent package-manager operations that could corrupt package state. Detect locks and explain when another operation is in progress.

## 6.4 Updates

Implement an update center that can:

- Check for available updates.
- List package names and versions.
- Show update summaries and security-related information where available.
- Update individual applications when supported.
- Update all eligible packages.
- Manage Flatpak updates.
- Display progress and logs.
- Report failures clearly.
- Notify the user when updates are available.
- Offer a controlled automatic-update option.
- Show when a restart is recommended or required.

Clearly distinguish application updates from operating-system updates.

Never promise rollback or atomic updates unless the selected underlying technology genuinely supports them.

## 6.5 Application details

Each application must have a dedicated details view containing relevant metadata, screenshots when available, release information, source details, and installation controls.

Provide useful filters for installed software, available software, updates, and software sources.

Build the interface around real data from the selected package and metadata systems.

Aether Store must remain useful even if an optional online catalog or external metadata service is unavailable.

---

# 7. SYSTEM SETTINGS

Build a unified Settings application called **Aether Settings**.

Use a clear navigation hierarchy, responsive layouts, search, and meaningful descriptions.

Implement actual controls for:

- Appearance.
- Display configuration.
- Audio.
- Network.
- Bluetooth.
- Keyboard.
- Mouse and touchpad.
- Printers where supported.
- Power management.
- Notifications.
- Applications.
- Default applications.
- Users and groups.
- Privacy.
- Accessibility.
- Date and time.
- Language and regional settings.
- Storage.
- System updates.
- Software sources.
- Security.
- Firewall configuration.
- Developer tools.
- Backup and recovery.
- About this system.

Integrate with the existing Linux system services wherever practical.

Settings must persist across restarts.

If a setting cannot be supported by the chosen backend, explain that limitation rather than displaying a fake toggle.

---

# 8. ORIGINAL APPLICATION SUITE

Develop a small, cohesive set of first-party applications that demonstrate the operating system's identity.

Prioritize quality over quantity.

Include:

- **Aether Files:** the custom file manager.
- **Aether Store:** the software manager.
- **Aether Studio:** desktop customization and theme management.
- **Aether Settings:** system configuration.
- **Aether Monitor:** CPU, memory, GPU, disk, network, process, and temperature monitoring where supported.
- **Aether Terminal:** a polished terminal emulator or a carefully integrated existing terminal.
- **Aether Update:** the system update interface, integrated with Aether Store where appropriate.
- **Aether Welcome:** first-boot setup, introductory guidance, and basic system checks.

Use existing mature applications when rebuilding them would provide little value. Integrate them visually and functionally where feasible.

Do not create empty applications just to fill an application menu.

---

# 9. SYSTEM MONITOR AND WIDGETS

Create a modular widget framework for the desktop.

Include optional widgets for:

- CPU utilization.
- Memory utilization.
- GPU utilization and temperature where supported.
- Storage usage.
- Network throughput.
- Clock and calendar.
- Weather through an optional online provider.
- Music playback controls.
- Audio visualization.
- System uptime.
- Battery status.
- Workspace information.

Widgets must be movable, resizable where appropriate, configurable, and removable.

Users should be able to change their appearance, update intervals, and displayed information.

Widgets must not secretly collect personal information or continuously poll hardware at unnecessarily high frequencies.

For GPU monitoring, support NVIDIA and AMD hardware where the required drivers and interfaces are available. Handle unsupported sensors gracefully.

---

# 10. SECURITY AND PRIVACY

Treat security as a core feature.

Implement sensible defaults:

- Signed operating-system packages.
- Signature verification for package repositories.
- Standard non-root user accounts.
- Proper privilege separation.
- Firewall integration.
- Secure handling of administrative operations.
- Sensible application permissions.
- Privacy controls for notifications, recent files, and usage data.
- No hidden telemetry.
- No unnecessary network services.
- No hardcoded passwords or API keys.
- No automatic execution of downloaded scripts.
- Safe temporary-file handling.
- Input validation.
- Dependency and license tracking.
- Clear security-update notifications.

If Flatpak is used, expose relevant permission information and provide a clear way to inspect application permissions.

Do not promise perfect isolation or absolute security.

Keep the base system as small as practical while preserving hardware compatibility and usability.

---

# 11. INSTALLER AND FIRST BOOT

Create a complete graphical installer with an identity consistent with AETHER OS.

The installer should support:

- UEFI installation.
- Automatic partitioning.
- Manual partitioning where feasible.
- Filesystem selection supported by the chosen installer.
- Bootloader configuration.
- Time zone selection.
- Keyboard layout selection.
- User account creation.
- Password entry.
- Installation progress.
- Error reporting.
- Reboot into the installed system.

Handle existing disks carefully. Clearly identify destructive operations and require explicit confirmation before erasing or repartitioning a disk.

Never assume that a particular disk is safe to erase.

Prefer integrating a proven installer and customizing its appearance and configuration over writing a complete partitioning engine from scratch.

After installation, Aether Welcome should guide the user through:

- Display configuration.
- Network setup.
- Theme selection.
- Wallpaper selection.
- Optional widget setup.
- Software repository configuration.
- System update checks.
- Basic desktop navigation.

The installed system should work without requiring an internet connection after all necessary installation packages have been acquired, although online features will naturally require connectivity.

---

# 12. PERFORMANCE AND HARDWARE SUPPORT

The operating system should remain responsive on ordinary desktop and laptop hardware.

Support x86-64 systems as the initial target.

Prioritize:

- Intel integrated graphics.
- AMD integrated and discrete graphics.
- NVIDIA graphics, including the RTX 2080 and RTX 5080 classes where compatible drivers and kernel support are available.
- Multiple monitors.
- High-refresh-rate displays.
- Mixed-resolution displays.
- Common USB peripherals.
- Wi-Fi and Ethernet.
- Common audio hardware.
- NVMe and SATA storage.
- Bluetooth devices.

Research the current driver situation for the selected Debian release.

Do not bundle proprietary drivers without checking redistribution rights. Explain any additional driver installation steps when necessary.

Use hardware acceleration when available.

Avoid continuously running animations when the desktop is idle.

Implement reduced-motion and low-resource modes.

Measure actual resource consumption rather than inventing performance figures.

---

# 13. DEVELOPMENT WORKFLOW AND AUTONOMY

You are responsible for the complete project lifecycle.

The user will not manually collect the Linux kernel, download source archives, prepare the dependency tree, or assemble the operating system by hand.

Proceed as follows.

## Phase 1: Inspect and plan

- Inspect the current development environment.
- Determine the available operating system, architecture, CPU, memory, storage, network access, privileges, and installed tools.
- Identify the latest Debian Stable release from official sources.
- Research compatible desktop technologies, compositors, package-management interfaces, and installer frameworks.
- Choose a realistic architecture.
- Create a project directory and a detailed implementation plan.
- Identify limitations and high-risk technical decisions.

Do not assume the development machine runs Linux. If it runs Windows, determine whether WSL2, a Linux virtual machine, or a dedicated Linux build environment is most appropriate.

Do not require the user to manually download a kernel or source archive.

## Phase 2: Acquire dependencies

Automatically obtain required source code, packages, tools, build systems, assets, and dependencies from trustworthy upstream sources.

Use official Debian repositories, official project repositories, and verified release artifacts.

For source archives and binaries, verify signatures or checksums when available and appropriate.

Record the source, version, license, and acquisition method of major dependencies.

Never execute arbitrary internet-downloaded scripts without inspection.

Avoid unnecessary external dependencies and services.

Do not fabricate download URLs, checksums, repository contents, or successful installation results.

If a download fails, diagnose the failure and try an appropriate alternative.

## Phase 3: Build a functioning foundation

Establish the bootable Debian-based system and verify the boot process.

Then implement the desktop shell, settings, theme engine, package manager integration, and original applications incrementally.

Build real functionality before adding decorative refinements.

Keep the operating system bootable throughout development whenever practical.

## Phase 4: Implement incrementally

Work in independently testable milestones.

At the end of each milestone:

- Compile the relevant components.
- Run available automated tests.
- Resolve build errors.
- Test the actual functionality.
- Update the documentation.
- Commit changes to version control when available.

Do not postpone all testing until the project is finished.

## 📊 DEVELOPMENT TRACKING

## Project Status: **35% Complete**

### Phase 1: Inspect and plan ✅ COMPLETED (100%)

**Completed Tasks:**
- ✅ Project scope and requirements reviewed from README.md
- ✅ Existing documentation analyzed (ARCHITECTURE.md, BUILD.md, DEBIAN_BASELINE.md, VM_TESTING.md)
- ✅ WSL2 environment verified (Debian 13 trixie, amd64)
- ✅ Build tools confirmed: qemu-system-x86, xorriso, apt, python3, live-build, debootstrap, qemu-utils
- ✅ Existing build artifacts reviewed (13 ISO test images in build/)
- ✅ Scripts directory reviewed (26 utility scripts)
- ✅ Tests directory reviewed (5 test files with VM testing framework)
- ✅ Initial project structure created (aether-os/)
- ✅ Setup scripts created (initial-setup.sh, setup-aether-config.sh)
- ✅ Aether Shell placeholder files created
- ✅ README.md updated with comprehensive progress tracking

**Key Achievements:**
- Debian 13 (trixie) base system confirmed and operational
- Live-build configuration established
- QEMU testing infrastructure fully operational
- Multiple test ISO images created and verified
- Development scripts and utilities established

---

## Phase 2: Acquire dependencies 🔄 IN PROGRESS (60%)

### Completed Tasks:
- ✅ Debian 13 (trixie) base system confirmed
- ✅ Live-build package installed and working
- ✅ QEMU testing infrastructure confirmed
- ✅ Python 3 environment available
- ✅ Project structure created
- ✅ Initial setup scripts created

### Pending Tasks:
- [ ] Complete dependency installation in WSL2
- [ ] Set up Aether-specific build configuration
- [ ] Create initial base ISO configuration
- [ ] Prepare first official Aether OS ISO

**Current State:**
- Build configuration backup system created
- Aether Shell configuration files created
- Aether apps configuration created
- Aether Welcome GTK first-run guide implemented; installed-system launch testing remains pending

---

## Phase 3: Build foundation 📋 PENDING (0%)

### Tasks:
- [ ] Configure live-build for Aether OS
- [ ] Create base ISO configuration files
- [ ] Set up initial root filesystem
- [ ] Configure bootloader (syslinux for BIOS, GRUB for UEFI)
- [ ] Build and verify first Aether OS ISO
- [ ] Run artifact verification tests

---

## Phase 4: Implement incrementally 📋 PENDING (0%)

### Aether Shell Components:
- [ ] Aether Dock (Plasma applet) - **STARTED** - Functional launcher/task switcher prototype; polish and customization verification remain
- [ ] Aether Taskbar
- [ ] Aether Launcher
- [ ] Aether Settings
- [ ] Aether Store
- [ ] Aether Files (file manager)
- [ ] Aether Monitor
- [ ] Aether Studio (theming)
- [ ] Aether Terminal
- [x] Aether Welcome (GTK first-run guide; first-login VM testing pending)
- [ ] Aether Update

### Desktop Environment:
- [ ] KDE Plasma 6 with KWin X11 configuration
- [ ] LightDM graphical greeter
- [ ] Theme engine implementation
- [ ] Window management integration
- [ ] Window effects and animations

---

## Phase 5: Integration and testing 📋 PENDING (0%)

### Tasks:
- [ ] VM tests for all components
- [x] BIOS and UEFI boot path testing (live ISO and installed-system boots verified in QEMU)
- [x] Taskbar live-session functionality testing (BIOS and UEFI; installed desktops also reached after installation)
- [x] Graphical greeter and live-user authentication testing (BIOS and UEFI; the live image auto-logs in on boot)
- [ ] First-boot experience testing
- [x] Installer persistence testing (BIOS and UEFI installs and repeat boots passed on separate disposable disks)
- [ ] Performance testing

---

## Phase 6: Polish and finalize 📋 PENDING (0%)

### Tasks:
- [ ] Security hardening
- [ ] Documentation completion
- [ ] User manual creation
- [ ] Final QA testing
- [ ] Release preparation

---

## 📋 QUICK STATUS SUMMARY

| Phase | Status | Progress |
|-------|--------|----------|
| 1. Inspect and plan | ✅ Done | 100% |
| 2. Acquire dependencies | 🔄 In Progress | 60% |
| 3. Build foundation | 📋 Pending | 0% |
| 4. Implement incrementally | 📋 Pending | 0% |
| 5. Integration and testing | 📋 Pending | 0% |
| 6. Polish and finalize | 📋 Pending | 0% |

---

## 📂 PROJECT STRUCTURE

```
AetherOS/
├── build/config/                       # Debian live-build configuration
├── docs/                               # Architecture, build, and VM-test docs
├── scripts/                            # Build, verification, and test helpers
├── shell/aether-dock/                  # Plasma-based Aether Dock
├── tests/                              # Unit and QEMU integration tests
└── README.md                           # Project vision, status, and roadmap
```

---

## 🎯 NEXT IMMEDIATE STEPS

### Short-term (This session):
1. ✅ Complete Phase 1 documentation ✅ DONE
2. [ ] Finish Phase 2 - Complete dependency acquisition
3. [ ] Begin Phase 3 - Create first official Aether OS ISO

### Immediate Actions:
1. Review and test the setup scripts created
2. Build the first official Aether OS ISO using existing configuration
3. Verify the ISO in QEMU
4. Begin implementation of Aether Dock (move from placeholder to full implementation)

### Longer-term Goals:
1. Implement remaining Aether Shell components
2. Integrate KDE Plasma 6 fully
3. Complete all application development
4. Comprehensive testing and QA
5. Security hardening and release preparation

---

## 📝 TODO TRACKING

### Immediate Next Tasks (Phase 2 completion):
- [ ] Test setup-aether-config.sh script
- [ ] Review Aether OS build configuration
- [ ] Complete any missing build tool installations

### Short-term Goals (Phase 3):
- [ ] Build first official Aether OS ISO
- [ ] Verify ISO structure and integrity
- [ ] Run artifact verification tests
- [ ] Test ISO boots in QEMU

### Medium-term Goals (Phase 4):
- [ ] Implement Aether Dock fully
- [ ] Implement Aether Settings
- [ ] Implement Aether Store
- [ ] Implement Aether Files
- [ ] Integrate with KDE Plasma 6

### Long-term Goals (Phases 5-6):
- [ ] Full integration testing
- [ ] Security audit
- [ ] Documentation completion
- [ ] User manual creation
- [ ] Final release preparation

---

## 📚 REFERENCES

- [README.md](README.md) - Project overview and requirements
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architecture decisions
- [BUILD.md](docs/BUILD.md) - Build workflow
- [DEBIAN_BASELINE.md](docs/DEBIAN_BASELINE.md) - Debian baseline info
- [VM_TESTING.md](docs/VM_TESTING.md) - VM testing procedures

### Completed Tasks:
- ✅ Assessed project scope and requirements
- ✅ Reviewed existing documentation (README.md, ARCHITECTURE.md, BUILD.md, DEBIAN_BASELINE.md, VM_TESTING.md)
- ✅ Verified WSL2 environment with Debian 13 (trixie)
- ✅ Confirmed available tools: qemu-system-x86, xorriso, apt, python3, live-build, debootstrap, qemu-utils
- ✅ Reviewed existing build artifacts (13 ISO images in build/)
- ✅ Reviewed existing scripts directory (23 scripts)
- ✅ Reviewed existing tests directory (5 test files)
- ✅ Created initial project structure in aether-os/
- ✅ Created setup scripts for configuration
- ✅ Created Aether Shell placeholder files
- ✅ Updated README.md with comprehensive progress tracking

### Current State Summary:
```
Project Root: repository root
WSL2 Environment: Debian 13 (trixie), amd64
Build System: Debian live-build configured
Current ISOs: 13 test images created
Scripts: 26 utility scripts (including new setup scripts)
Tests: 5 test files including VM testing framework
```

## Phase 2: Acquire dependencies 🔄 IN PROGRESS

### Completed Tasks:
- ✅ Verified Debian 13 (trixie) base system
- ✅ Confirmed live-build is installed and working
- ✅ Confirmed qemu-system-x86_64 and xorriso are available
- ✅ Confirmed Python 3 is available

### Pending Tasks:
- [ ] Install additional build tools in WSL2 (if needed)
- [ ] Set up Aether-specific build configuration under build/
- [ ] Configure live-build for Aether OS customization
- [ ] Set up initial package configuration
- [ ] Prepare initial base ISO configuration

## Phase 3: Build foundation 📋 PENDING

### Tasks:
- [ ] Create base ISO configuration files
- [ ] Configure live-build for Aether OS
- [ ] Set up initial root filesystem
- [ ] Configure bootloader (syslinux for BIOS, GRUB for UEFI)
- [ ] Create initial bootable ISO
- [ ] Verify ISO structure and artifact integrity

## Phase 4: Implement incrementally 📋 PENDING

### Aether Shell Components:
- [ ] Implement Aether Dock (Plasma applet)
- [ ] Implement Aether Taskbar
- [ ] Implement Aether Launcher
- [ ] Implement Aether Settings
- [ ] Implement Aether Store
- [ ] Implement Aether Files (file manager)
- [ ] Implement Aether Monitor
- [ ] Implement Aether Studio (theming)
- [ ] Implement Aether Terminal
- [x] Implement Aether Welcome (GTK first-run guide with links to existing desktop tools)
- [ ] Implement Aether Update

### Desktop Environment:
- [ ] Configure KDE Plasma 6 with KWin X11
- [ ] Configure LightDM graphical greeter
- [ ] Set up theme engine
- [ ] Configure window management
- [ ] Implement window effects and animations

## Phase 5: Integration and testing 📋 PENDING

### Tasks:
- [ ] Run VM tests for all components
- [x] Test BIOS and UEFI boot paths (live ISO and installed-system boots verified in QEMU)
- [x] Test live taskbar functionality (BIOS and UEFI; installed desktops also reached after installation)
- [x] Test graphical greeter and live-user authentication (BIOS and UEFI; fresh live boot still auto-logs in)
- [ ] Test first-boot experience (Aether Welcome is implemented; validate installed-session autostart and completion persistence)
- [x] Test installer persistence (BIOS and UEFI installs and repeat boots passed on separate disposable disks)
- [ ] Performance testing and optimization

## Phase 6: Polish and finalize 📋 PENDING

### Tasks:
- [ ] Security hardening
- [ ] Documentation completion
- [ ] User manual creation
- [ ] Final quality assurance testing
- [ ] Release preparation

---

# 📊 PROJECT STATUS SUMMARY

## Overall Progress: **30% Complete**

| Phase | Status | Completion |
|-------|--------|------------|
| 1. Inspect and plan | ✅ Done | 100% |
| 2. Acquire dependencies | 🔄 In Progress | 50% |
| 3. Build foundation | 📋 Pending | 0% |
| 4. Implement incrementally | 📋 Pending | 0% |
| 5. Integration and testing | 📋 Pending | 0% |
| 6. Polish and finalize | 📋 Pending | 0% |

## Key Achievements:
- ✅ Debian 13 (trixie) base system confirmed
- ✅ Live-build configuration established
- ✅ QEMU testing framework operational
- ✅ 13 ISO test images built and verified
- ✅ Comprehensive testing infrastructure in place
- ✅ Development scripts and utilities created

## Next Immediate Steps:
1. Finalize build configuration for Aether OS customization
2. Create first official Aether OS ISO (not just test images)
3. Begin implementation of Aether Dock component
4. Set up KDE Plasma 6 with custom Aether Shell integration

---

# 📝 TODO TRACKING

### Immediate Next Tasks (Phase 2 completion):
- [ ] Review and complete missing build tool installations
- [ ] Create Aether-specific build configuration
- [ ] Set up custom live-build hooks for Aether OS

### Short-term Goals (Phase 3):
- [ ] Build first official Aether OS ISO
- [ ] Verify ISO boots correctly
- [ ] Test basic system functionality

### Medium-term Goals (Phase 4):
- [ ] Implement core Aether Shell components
- [ ] Integrate KDE Plasma 6 with customizations
- [ ] Create Aether Dock and taskbar

### Long-term Goals (Phases 5-6):
- [ ] Full integration testing
- [ ] Security and performance optimization
- [ ] Documentation and release preparation


Test the desktop and system in a disposable virtual machine before testing on physical hardware.

Verify:

- Boot and login.
- Desktop startup.
- Window management.
- Application launching.
- Multi-monitor behavior where the test environment permits it.
- Theme changes.
- Configuration persistence.
- File management.
- Software installation and removal.
- System and application updates.
- Network connectivity.
- Audio where testable.
- Permission handling.
- Failure recovery.
- Installer behavior.
- Reboot persistence.

Use screenshots and real execution results to evaluate the visual quality.

Do not claim a feature works merely because the relevant source code exists.

## Phase 6: Produce release artifacts

Create a reproducible build pipeline and generate the appropriate bootable installation image.

Provide:

- A bootable ISO.
- A reproducible build configuration.
- The project source code.
- Dependency manifests.
- Build and installation scripts.
- A software bill of materials where practical.
- Automated tests.
- Documentation.
- Known limitations.
- Checksums for the generated release artifacts.
- Instructions for testing in a virtual machine.
- Instructions for installing on physical hardware.

If the full distribution cannot be completed in one execution, deliver a working, tested milestone and continue from the existing project rather than pretending the entire OS is finished.

---

# 14. CODE QUALITY AND ARCHITECTURE

Organize the repository into clearly separated components.

Suggested structure:

aether-os/

- build/
- installer/
- system/
- shell/
- applications/
- store/
- settings/
- themes/
- wallpapers/
- widgets/
- packaging/
- tests/
- docs/
- scripts/

Adapt this structure when justified, but maintain clear boundaries between system integration, user interfaces, privileged operations, and reusable components.

Requirements:

- Consistent naming.
- Clear interfaces between components.
- Structured logging.
- Meaningful error handling.
- Automated tests for critical functionality.
- Secure handling of system operations.
- No hardcoded machine-specific paths when avoidable.
- No unnecessary duplication.
- No giant monolithic source files.
- No fake implementations masquerading as finished features.
- No placeholder buttons in released applications.
- No abandoned build errors silently ignored.
- No unnecessary dependencies.

Use version control and maintain a clear project history where possible.

Document architectural decisions so future development can continue without reconstructing the entire project from scratch.

---

# 15. DESIGN QUALITY GATE

Before declaring any major interface complete, evaluate it against these criteria:

1. Does it have a coherent visual identity?
2. Does its layout feel intentional and professionally composed?
3. Are typography, spacing, icons, colors, and controls consistent?
4. Does it work at different screen resolutions and scaling levels?
5. Does it respond quickly to user input?
6. Are all visible controls functional?
7. Does it handle empty states, loading states, and errors properly?
8. Does it integrate with the rest of AETHER OS?
9. Can users customize it?
10. Does it avoid unnecessary visual clutter?

If an interface looks like a generic AI-generated dashboard, redesign it before proceeding.

Do not compensate for poor layout with gradients, glow effects, blur, or excessive rounded corners.

Use a deliberate visual hierarchy, appropriate negative space, high-quality icons, carefully selected typography, and consistent interaction patterns.

Use original artwork and real screenshots of the running system when evaluating the result.

---

# 16. ACCEPTANCE CRITERIA

AETHER OS is not complete until it has demonstrated the following:

- A bootable Debian-based operating system.
- A functioning graphical login.
- An original, integrated desktop shell.
- A customizable taskbar and application launcher.
- Functional window management and workspaces.
- A real file manager or a carefully integrated equivalent.
- A working system settings application.
- A persistent theme engine and desktop customization application.
- Multiple original wallpapers and working wallpaper controls.
- A software store that installs, removes, and describes real applications.
- Working package and application update workflows.
- A functional system monitor.
- Real integration with the underlying Linux system.
- A reproducible build process.
- A generated installation image.
- A successful virtual-machine boot test.
- Documented limitations and verified test results.

Distinguish between implemented, tested, partially supported, and unimplemented features.

Do not declare acceptance criteria complete without evidence.

---

# 17. FINAL OPERATING INSTRUCTIONS

Begin now.

First inspect the available environment and research the official Debian Stable release. Choose the architecture and tools, acquire the required dependencies, create the repository, and begin implementation.

Do not ask the user to choose every framework, library, icon pack, or architectural detail. Make sensible decisions independently and explain important trade-offs briefly.

Do not stop after producing a plan, a desktop mockup, a website, or a prototype that only resembles the intended interface.

Build toward a real, bootable operating system.

Prioritize a reliable foundation, then a polished desktop shell, then the customization engine and software store, followed by the remaining applications and refinements.

If you encounter a blocker, investigate it, attempt reasonable alternatives, and continue with independent tasks. Ask the user only when an essential decision, unavailable permission, or genuinely inaccessible resource prevents further progress.

Protect the host system. Never erase disks, overwrite bootloaders, modify partitions, or perform destructive system operations without explicit authorization.

**The ultimate objective is to create a complete, original, futuristic, deeply customizable Linux distribution that feels like a next-generation desktop operating system, uses Debian for stability, and delivers real functionality rather than just an attractive screenshot.**

## 18. IMPLEMENTATION STATUS (2026-10-28)

### What is done
- README.md build specification read and understood.
- Debian 13 (trixie) selected as base (current stable, point release 13.7, EOL 2028-08-09, LTS to 2030-06-30).
- Architecture documented in `docs/ARCHITECTURE.md` (hybrid BIOS/UEFI live ISO, ext4 installation target, systemd, Wayland-first, sway/wlroots, GTK4/Qt6 shell).
- Debian baseline documented in `docs/DEBIAN_BASELINE.md`.
- Repository structure scaffolded per §14: `build/`, `installer/`, `system/`, `shell/`, `applications/`, `store/`, `settings/`, `themes/`, `wallpapers/`, `widgets/`, `packaging/`, `tests/`, `docs/`, `scripts/`.
- live-build configuration written and validated: `build/auto/config` (trixie, amd64, hybrid BIOS/UEFI ISO, non-free firmware, security+updates mirrors; `noauto` prevents recursive configuration).
- Package list is transitioning to KDE Plasma 6 with KWin/X11, LightDM, Plasma network/audio controls, Dolphin, and Konsole. KDE is being used as a customizable platform while original Aether shell components are developed; the project goal remains a distinct shell rather than a rebranded stock desktop.
- Build tooling installed in WSL2: `lb`, `debootstrap`, `qemu-img`, `qemu-system-x86_64`, `xorriso`, `git`, `python3`, `node`.
- WSL2 environment verified (Debian 13 trixie distro, kernel 6.18.54, sudo prompts for local credentials).
- First live ISO build completed successfully: `build/live-image-amd64.hybrid.iso` (2,210,267,136 bytes). El Torito inspection confirms BIOS and UEFI boot entries; a headless QEMU BIOS run reached the ISOLINUX bootloader. The user reports that the ISO also appears to work correctly in VirtualBox. SHA-256: `514EE69F14364C4B1632471293B04BB35B30BE9FDE487C674711011C3F07F393` (recorded in `build/live-image-amd64.hybrid.iso.sha256`).
- Added `scripts/verify_live_iso.py` and focused tests. The verifier checks the adjacent SHA-256 manifest, expected volume ID, BIOS/UEFI boot entries, and live root filesystem marker. On 2026-10-28, the original and XFCE test images passed; xorriso reported volume `AETHER_OS_13`, BIOS `/isolinux/isolinux.bin`, UEFI `/boot/grub/efi.img`, and `/live/filesystem.squashfs`. All 16 focused unit tests pass as of 2026-10-30. These checks do not establish installation or reboot persistence.
- QEMU 10.0.13 smoke tests reached the original ISO's live boot menu in both BIOS and UEFI modes; its BIOS live entry reached a tty7 text login. A greetd/gtkgreet/Sway attempt showed a black display and was replaced by XFCE4, Xorg, and LightDM. The separate `build/live-image-amd64.xfce-test.iso` was booted read-only in QEMU with no virtual disk. Through BIOS firmware, LightDM auto-logged into the live user and the XFCE wallpaper, panels, and a rendered XFCE Terminal window were visible. The first UEFI test showed the XFCE background and desktop icons but no panels. Testing confirmed the graphical session was on VT7 while UEFI left the guest on a text VT; manually switching to VT7 made the full desktop visible. A new test image, `build/live-image-amd64.xfce-vt-test.iso`, adds a delayed systemd service to activate VT7. Its UEFI boot showed the complete desktop and panels without manual intervention. This verifies the live desktop through BIOS and UEFI in QEMU. The live image auto-logs in, so the graphical greeter is not verified. Installation and reboot persistence remain unverified; no virtual hard disk was attached or modified.
- Added the initial Aether Dock Plasma 6 applet under `shell/aether-dock/`. It uses Plasma's task model for pinned application launching and live-window activation/minimization, and offers settings for pinned app IDs, icon size, spacing, corner radius, opacity, and accent color.
- Fixed the dock's task-row sizing and removed a read-only `Row.implicitWidth` assignment found during BIOS QEMU testing. Added regression coverage; all 20 Python tests and shell syntax checks pass.
- Added a one-time LightDM session setup hook to seed the custom Plasma panel for the live user without overwriting later panel customization. BIOS testing of `build/live-image-amd64.plasma-aether-test7.iso` confirmed the applet entry and seed marker in the live user's config, with no Aether-specific journal errors.
- Added an original Aether icon theme with custom Dolphin, terminal, System Settings, and launcher icons, inheriting Breeze for other applications. Set Aether as the KDE and LightDM icon-theme default; a first-session action applies the Aether wallpaper once while preserving later user wallpaper choices. BIOS QEMU testing of `build/live-image-amd64.aether-taskbar-test11.iso` visually confirmed the Aether wallpaper and custom dock icons.
- Revised the taskbar seed to use expanding spacers around the Aether Dock, explicit Dolphin/Konsole/System Settings pins, a centered dock, and a right-aligned system tray/clock. The latest image, `build/live-image-amd64.aether-taskbar-test13.iso`, passed ISO verification and booted to Plasma in BIOS and UEFI QEMU using KVM, read-only ISO media, and no virtual disk. Automated UEFI checks confirmed dock icons, app launch, minimize/restore, and launching another pinned app. In BIOS, changing the pin list to Konsole, applying it, reopening settings to confirm the value remained, and launching Konsole from the updated dock all succeeded in the live session. BIOS and UEFI greeter tests rendered LightDM and authenticated the live account successfully; the normal live boot still auto-logs in.
- The configured Debian Live Installer completed BIOS and UEFI installations in separate QEMU runs, each targeting only its explicitly approved disposable 32 GiB QCOW2 disk. The BIOS-installed system booted and authenticated, then did so again from the same disk in a later QEMU session. The UEFI installer created a FAT32 EFI System Partition, ext4 root, and swap on the sole target disk; the installed system booted to LightDM and Plasma and authenticated in two separate QEMU sessions using that disk. UEFI boot verification used the same disk attached through QEMU's SATA controller with read-only non-bootable media, allowing firmware to fall through to the installed disk. No host disk was attached or changed. Real hardware and other firmware implementations remain untested.
- Added the GTK Aether Welcome app, a launcher entry, and an installed-session first-run autostart that skips live sessions and stores per-user completion. `build/aether-welcome-test2.iso` passed checksum/BIOS/UEFI structure verification and reached the live desktop in UEFI QEMU with no virtual disk attached. Manually opening Aether Welcome rendered its Welcome and setup pages. The live image still displayed KDE's generic Welcome Center at startup, and the installed first-run autostart/completion flow has not yet been tested; keep first-boot testing open.
- Added `scripts/create-virtualbox-test-vm.ps1` for a checksum-verified VirtualBox review VM using the current Welcome-test ISO, UEFI, NAT networking, and a fresh dynamically allocated 32 GB virtual disk. The profile is registered locally but not started; it has no host disk passthrough or shared folders.

### What needs to be done
- **Highest priority — finish Aether Welcome first-run integration.** The GTK guide is implemented and its Welcome and setup pages rendered in UEFI QEMU, but installed-system autostart and completion persistence are not yet verified. The live ISO still opens KDE's generic Welcome Center despite the existing suppression config, so investigate that competing startup path before calling the replacement complete. Verify first-login launch and repeat-login behavior only in an explicitly approved disposable VM; never target host storage.
- BIOS and UEFI greeter validation is complete: the LightDM prompt renders when opened from the live session, and the live account (`user` / `live`) authenticates and returns to Plasma. Initial live boot remains automatic login.
- The taskbar live-session milestone is verified on `aether-taskbar-test13.iso`: BIOS and UEFI boot, configured pins, app launch, minimize/restore, editable pins, and Aether wallpaper/custom icons. Installed Plasma desktops were also reached after both BIOS and UEFI installation tests.
- Continue Aether Shell development (notification center, window management, workspaces, lock screen).
- Build first-party apps: Aether Files, Aether Store, Aether Studio, Aether Settings, Aether Monitor, Aether Terminal, and Aether Update. Aether Welcome's initial GTK guide is implemented; its installed first-run behavior still needs VM validation and further polish.
- Implement the theme engine, desktop-layout presets, wallpaper manager.
- Integrate APT + Flatpak in Aether Store with real install/remove/update flows.
- Create original wallpapers, icon themes, cursor themes.
- Build installer (Calamares or Debian installer), recovery tools.
- Write automated tests for critical functionality.
- Produce final documentation, repeatable VM test evidence, and acceptance-criteria checklist.
\
