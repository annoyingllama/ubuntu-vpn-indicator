#!/usr/bin/python3

import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import gi
import psutil

gi.require_version('AppIndicator3', '0.1')

from gi.repository import AppIndicator3, Gtk


def check_state():
    cmd = f"systemctl is-active {indicator_id}"
    return subprocess.run([cmd], stdout=subprocess.PIPE, shell=True).stdout.decode().strip()


def report_state():
    state = check_state()
    subprocess.Popen(["notify-send", f"{indicator_id} is {state}"])


def update_state(action):
    subprocess.call(['sudo', 'systemctl', f'{action}', f'{indicator_id}'])


def get_icon_path(state=None):
    if state is None:
        state = check_state()

    if state == "active":
        icon_path = os.path.join(project_path, "icons/vpnon.png")
    else:
        icon_path = os.path.join(project_path, "icons/vpnoff.png")
    return icon_path


class StateTracker(threading.Thread):
    def __init__(self, init_state):
        super().__init__()
        self.known_state = init_state
        self.exit = False

    def run(self):
        while self.exit is False:
            state = check_state()
            if state != self.known_state:
                icon_path = get_icon_path(state)
                indicator.set_icon(icon_path)
                report_state()
                self.known_state = state
            time.sleep(5)
        return


def up(*args):
    state = check_state()
    if state == "inactive":
        update_state("start")
        indicator.set_icon(get_icon_path("active"))
        worker.known_state = "active"
    time.sleep(2)
    report_state()
    return


def down(*args):
    state = check_state()
    if state == "active":
        update_state("stop")
        indicator.set_icon(get_icon_path("inactive"))
        worker.known_state = "inactive"
    time.sleep(2)
    report_state()
    return


def close(*args):
    update_state("stop")
    time.sleep(2)
    report_state()
    Gtk.main_quit()
    os.unlink(pid_file)


def build_menu():
    menu = Gtk.Menu()

    vpn_up = Gtk.MenuItem('Connect')
    vpn_up.connect('activate', up)
    menu.append(vpn_up)

    vpn_down = Gtk.MenuItem('Disconnect')
    vpn_down.connect('activate', down)
    menu.append(vpn_down)

    vpn_quit = Gtk.MenuItem('Exit')
    vpn_quit.connect('activate', close)
    menu.append(vpn_quit)

    menu.show_all()
    return menu


if __name__ == "__main__":
    indicator_id = sys.argv[1]
    project_path = Path(__file__).parent
    pid = str(os.getpid())
    pid_file = f"{project_path}/process.pid"
    if os.path.isfile(pid_file):
        with open(pid_file, 'r') as f:
            old_pid = f.read()
        if psutil.pid_exists(int(old_pid)):
            subprocess.Popen(["notify-send", "vpn indicator is already running"])
            sys.exit()

    with open(pid_file, 'w') as f:
        f.write(pid)

    try:
        worker = StateTracker(init_state=check_state())
        worker.start()

        init_icon_path = get_icon_path()
        indicator = AppIndicator3.Indicator.new(id=indicator_id,
                                                icon_name=init_icon_path,
                                                category=AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
        indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        indicator.set_menu(build_menu())
        Gtk.main()
    finally:
        worker.exit = True
        worker.join()
        os.unlink(pid_file)
