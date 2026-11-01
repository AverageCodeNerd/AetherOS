#!/usr/bin/env python3
"""Drive an AETHER OS live ISO in QEMU through QMP.

The helper keeps one VM session alive between invocations so screenshots and
input can be issued from separate commands:

    python3 tests/qemu_session.py start --iso build/live-image-amd64.iso
    python3 tests/qemu_session.py wait --timeout 180
    python3 tests/qemu_session.py shot desktop
    python3 tests/qemu_session.py click 960 1040
    python3 tests/qemu_session.py stop
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEFAULT_STATE = Path("/var/tmp/aether-qemu-session.json")
OVMF_CODE = Path("/usr/share/OVMF/OVMF_CODE_4M.fd")
OVMF_VARS = Path("/usr/share/OVMF/OVMF_VARS_4M.fd")


class QmpError(RuntimeError):
    pass


class QmpClient:
    def __init__(self, socket_path: str, timeout: float = 30.0) -> None:
        deadline = time.monotonic() + timeout
        while True:
            try:
                self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self._sock.connect(socket_path)
                break
            except OSError:
                self._sock.close()
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.2)
        self._sock.settimeout(60)
        self._stream = self._sock.makefile("rwb")
        self._read()
        self.command("qmp_capabilities")

    def _read(self) -> dict:
        line = self._stream.readline()
        if not line:
            raise QmpError("QMP connection closed")
        message = json.loads(line)
        if "error" in message:
            raise QmpError(message["error"].get("desc", str(message["error"])))
        return message

    def command(self, execute: str, **arguments):
        payload = {"execute": execute}
        if arguments:
            payload["arguments"] = arguments
        self._stream.write((json.dumps(payload) + "\n").encode())
        self._stream.flush()
        while True:
            message = self._read()
            if "event" in message:
                continue
            if "return" in message:
                return message["return"]
            raise QmpError(f"unexpected QMP message: {message}")

    def hmp(self, command: str) -> str:
        return self.command("human-monitor-command", **{"command-line": command})

    def close(self) -> None:
        try:
            self._stream.close()
        finally:
            self._sock.close()

    def __enter__(self) -> "QmpClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()


def load_state(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"No VM session at {path}. Start one with the 'start' command.")
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def connect(state: dict) -> QmpClient:
    return QmpClient(state["qmp"])


def write_ppm(state: dict, name: str) -> Path:
    outdir = Path(state["outdir"])
    outdir.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(char if char.isalnum() or char in "._-" else "_" for char in name)
    ppm = outdir / f"{safe_name}.ppm"
    with connect(state) as qmp:
        # Use the QMP command rather than the HMP "screendump" monitor command:
        # HMP splits its command line on whitespace, which corrupts paths that
        # contain spaces (the project directory is "Windows 12 iso").
        qmp.command("screendump", filename=str(ppm))
    return ppm


def ppm_to_png(state: dict, ppm: Path) -> Path:
    from PIL import Image

    png = ppm.with_suffix(".png")
    with Image.open(ppm) as image:
        image.save(png)
        state["width"], state["height"] = image.size
    ppm.unlink(missing_ok=True)
    return png


def start(args: argparse.Namespace) -> None:
    iso = Path(args.iso).resolve()
    if not iso.is_file():
        raise SystemExit(f"ISO not found: {iso}")
    if args.uefi and not OVMF_CODE.is_file():
        raise SystemExit(f"OVMF firmware not found: {OVMF_CODE}")

    state_path = Path(args.state)
    if state_path.is_file():
        previous = load_state(state_path)
        if is_running(previous):
            raise SystemExit(
                f"A VM session is already running (pid {previous['pid']}). "
                "Stop it first."
            )

    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    session_dir = Path(tempfile.mkdtemp(prefix="aether-qemu-", dir="/var/tmp"))
    qmp_socket = session_dir / "qmp.sock"
    log_path = outdir / f"qemu-{'uefi' if args.uefi else 'bios'}.log"
    use_kvm = os.access("/dev/kvm", os.R_OK | os.W_OK)

    command = [
        "qemu-system-x86_64",
        "-name",
        f"aether-os-{'uefi' if args.uefi else 'bios'}",
        "-machine",
        "q35,accel=kvm" if use_kvm else "q35,accel=tcg",
        "-cpu",
        "host" if use_kvm else "qemu64",
        "-m",
        str(args.memory),
        "-smp",
        str(args.cpus),
        "-display",
        "none",
        "-device",
        f"VGA,edid=on,xres={args.width},yres={args.height},vgamem_mb=64",
        "-device",
        "qemu-xhci,id=xhci",
        "-device",
        "usb-tablet,bus=xhci.0",
        "-drive",
        f"file={iso},media=cdrom,readonly=on",
        "-boot",
        "order=d,menu=on",
        "-no-reboot",
        "-nic",
        "user,model=e1000",
        "-qmp",
        f"unix:{qmp_socket},server,nowait",
    ]

    if args.uefi:
        vars_copy = session_dir / "OVMF_VARS.fd"
        shutil.copyfile(OVMF_VARS, vars_copy)
        command += [
            "-drive",
            f"if=pflash,format=raw,readonly=on,file={OVMF_CODE}",
            "-drive",
            f"if=pflash,format=raw,file={vars_copy}",
        ]

    if args.extra:
        command += args.extra

    log_handle = log_path.open("wb")
    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    state = {
        "pid": process.pid,
        "qmp": str(qmp_socket),
        "session_dir": str(session_dir),
        "outdir": str(outdir),
        "firmware": "uefi" if args.uefi else "bios",
        "iso": str(iso),
        "width": args.width,
        "height": args.height,
        "started": time.time(),
        "log": str(log_path),
    }
    save_state(state_path, state)

    deadline = time.monotonic() + 30
    while True:
        if process.poll() is not None:
            raise SystemExit(
                f"QEMU exited with code {process.returncode}. See {log_path}."
            )
        if qmp_socket.exists():
            try:
                with connect(state) as qmp:
                    qmp.command("query-status")
                break
            except (OSError, QmpError):
                pass
        if time.monotonic() >= deadline:
            raise SystemExit(f"QMP did not become available. See {log_path}.")
        time.sleep(0.3)

    print(f"Started {state['firmware']} VM: pid {process.pid} accel={'kvm' if use_kvm else 'tcg'}")
    print(f"Log: {log_path}")
    print(f"State: {state_path}")


def is_running(state: dict) -> bool:
    try:
        os.kill(state["pid"], 0)
    except OSError:
        return False
    return True


def wait(args: argparse.Namespace) -> None:
    state = load_state(Path(args.state))
    if not is_running(state):
        raise SystemExit("The VM process is not running.")
    deadline = time.monotonic() + args.timeout
    last_signature = None
    stable = 0
    while time.monotonic() < deadline:
        ppm = write_ppm(state, "wait")
        try:
            from PIL import Image, ImageStat

            with Image.open(ppm) as image:
                grayscale = image.convert("L")
                stat = ImageStat.Stat(grayscale)
                mean = stat.mean[0]
                dark = sum(1 for pixel in grayscale.getdata() if pixel < 8) / (
                    image.width * image.height
                )
                signature = (round(mean, 1), round(dark, 3), image.size)
        finally:
            ppm.unlink(missing_ok=True)
        print(f"mean={signature[0]} dark={signature[1]} size={signature[2]}")
        if signature == last_signature:
            stable += 1
        else:
            stable = 0
        last_signature = signature
        if args.require_desktop:
            # A Plasma desktop includes bright text and panel details; a black
            # or text-console boot screen does not. Require the screen to stay
            # unchanged across two samples as well.
            if signature[0] > args.min_mean and stable >= 2:
                print("Desktop appears ready.")
                return
        else:
            if stable >= 2:
                print("Screen stopped changing.")
                return
        time.sleep(args.interval)
    raise SystemExit("Timed out waiting for the guest screen.")


def shot(args: argparse.Namespace) -> None:
    state = load_state(Path(args.state))
    ppm = write_ppm(state, args.name)
    png = ppm_to_png(state, ppm)
    save_state(Path(args.state), state)
    print(png)


def move(args: argparse.Namespace) -> None:
    state = load_state(Path(args.state))
    width, height = args.width or state["width"], args.height or state["height"]
    x = max(0, min(32767, round(args.x / width * 32767)))
    y = max(0, min(32767, round(args.y / height * 32767)))
    with connect(state) as qmp:
        qmp.command(
            "input-send-event",
            events=[
                {"type": "abs", "data": {"axis": "x", "value": x}},
                {"type": "abs", "data": {"axis": "y", "value": y}},
            ],
        )


def click(args: argparse.Namespace) -> None:
    state = load_state(Path(args.state))
    width, height = args.width or state["width"], args.height or state["height"]
    x = max(0, min(32767, round(args.x / width * 32767)))
    y = max(0, min(32767, round(args.y / height * 32767)))
    with connect(state) as qmp:
        button = args.button
        qmp.command(
            "input-send-event",
            events=[
                {"type": "abs", "data": {"axis": "x", "value": x}},
                {"type": "abs", "data": {"axis": "y", "value": y}},
                {"type": "btn", "data": {"down": True, "button": button}},
            ],
        )
        time.sleep(0.08)
        qmp.command(
            "input-send-event",
            events=[{"type": "btn", "data": {"down": False, "button": button}}],
        )
    print(f"Clicked {args.x},{args.y} ({button})")


KEY_NAMES = {
    " ": "spc",
    ".": "dot",
    "/": "slash",
    "-": "minus",
    "_": "shift-minus",
    ":": "shift-semicolon",
    "=": "equal",
    "\n": "ret",
}


def key(args: argparse.Namespace) -> None:
    state = load_state(Path(args.state))
    with connect(state) as qmp:
        qmp.hmp("sendkey " + "-".join(args.keys))
    print("Sent key " + "-".join(args.keys))


def type_text(args: argparse.Namespace) -> None:
    state = load_state(Path(args.state))
    with connect(state) as qmp:
        for char in args.text:
            key_name = KEY_NAMES.get(char, char)
            qmp.hmp("sendkey " + key_name)
            time.sleep(0.03)
    print(f"Typed {args.text!r}")


def status(args: argparse.Namespace) -> None:
    state = load_state(Path(args.state))
    running = is_running(state)
    print(f"pid={state['pid']} running={running} firmware={state['firmware']}")
    if running:
        try:
            with connect(state) as qmp:
                print(qmp.command("query-status"))
        except (OSError, QmpError) as error:
            print(f"QMP unavailable: {error}")
    sys.exit(0 if running else 1)


def stop(args: argparse.Namespace) -> None:
    state_path = Path(args.state)
    state = load_state(state_path)
    if is_running(state):
        try:
            with connect(state) as qmp:
                qmp.command("quit")
        except (OSError, QmpError):
            pass
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and is_running(state):
            time.sleep(0.2)
        if is_running(state):
            os.kill(state["pid"], signal.SIGTERM)
    session_dir = state.get("session_dir")
    if session_dir and session_dir.startswith("/var/tmp/aether-qemu-"):
        shutil.rmtree(session_dir, ignore_errors=True)
    if state_path.exists() and not args.keep_state:
        state_path.unlink()
    print("Stopped VM session.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", default=str(DEFAULT_STATE))
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="boot an ISO")
    start_parser.add_argument("--iso", required=True)
    start_parser.add_argument("--uefi", action="store_true")
    start_parser.add_argument("--outdir", default="tests/results")
    start_parser.add_argument("--memory", type=int, default=4096)
    start_parser.add_argument("--cpus", type=int, default=4)
    start_parser.add_argument("--width", type=int, default=1920)
    start_parser.add_argument("--height", type=int, default=1080)
    start_parser.add_argument(
        "--extra", nargs=argparse.REMAINDER, help="extra qemu arguments"
    )
    start_parser.set_defaults(func=start)

    wait_parser = subparsers.add_parser("wait", help="wait for the desktop")
    wait_parser.add_argument("--timeout", type=float, default=240)
    wait_parser.add_argument("--interval", type=float, default=10)
    wait_parser.add_argument("--require-desktop", action="store_true")
    wait_parser.add_argument("--min-mean", type=float, default=8.0)
    wait_parser.set_defaults(func=wait)

    shot_parser = subparsers.add_parser("shot", help="capture a PNG screenshot")
    shot_parser.add_argument("name")
    shot_parser.set_defaults(func=shot)

    move_parser = subparsers.add_parser("move", help="move the pointer")
    move_parser.add_argument("x", type=int)
    move_parser.add_argument("y", type=int)
    move_parser.add_argument("--width", type=int)
    move_parser.add_argument("--height", type=int)
    move_parser.set_defaults(func=move)

    click_parser = subparsers.add_parser("click", help="click at guest pixels")
    click_parser.add_argument("x", type=int)
    click_parser.add_argument("y", type=int)
    click_parser.add_argument("--width", type=int)
    click_parser.add_argument("--height", type=int)
    click_parser.add_argument(
        "--button",
        choices=("left", "middle", "right"),
        default="left",
    )
    click_parser.set_defaults(func=click)

    key_parser = subparsers.add_parser("key", help="send an HMP key combo")
    key_parser.add_argument("keys", nargs="+")
    key_parser.set_defaults(func=key)

    type_parser = subparsers.add_parser("type", help="type text with sendkey")
    type_parser.add_argument("text")
    type_parser.set_defaults(func=type_text)

    subparsers.add_parser("status", help="show VM status").set_defaults(func=status)

    stop_parser = subparsers.add_parser("stop", help="stop the VM")
    stop_parser.add_argument("--keep-state", action="store_true")
    stop_parser.set_defaults(func=stop)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
