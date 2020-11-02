#!/usr/bin/python3
import os
import subprocess
import sys
import time
from pathlib import Path

import gi

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


def up(*args):
    state = check_state()
    if state == "inactive":
        update_state("start")
        indicator.set_icon(os.path.join(project_path, "icons/vpnon.png"))
    time.sleep(2)
    report_state()
    return


def down(*args):
    state = check_state()
    if state == "active":
        update_state("stop")
        indicator.set_icon(os.path.join(project_path, "icons/vpnoff.png"))
    time.sleep(2)
    report_state()
    return


def close(*args):
    update_state("stop")
    time.sleep(2)
    report_state()
    Gtk.main_quit()


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
    init_state = check_state()
    if init_state == "active":
        init_icon_path = os.path.join(project_path, "icons/vpnon.png")
    else:
        init_icon_path = os.path.join(project_path, "icons/vpnoff.png")

    indicator = AppIndicator3.Indicator.new(id=indicator_id,
                                            icon_name=init_icon_path,
                                            category=AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    Gtk.main()
