
An openvpn status indicator icon for ubuntu with drop down control menu.
It monitors and controls the state of openvpn@yourvpn.service

![image alt <](Screenshot.png)

This project creates a gtk app indicator and a desktop entry to start it.
You can also add the python script to your start up applications

You will need an yourvpn.ovpn config file that works with ```sudo openvpn --config yourvpn.ovpn```

Instructions:
1. cd to project directory
2. run setup.sh
3. it will ask for path to your config file and you have to choose a name for your vpn indicator
3. follow interactive instructions

This script
1. creates an entry in /etc/openvpn for yourvpn, so you can control the vpn with systemctl
2. create a .desktop entry and places it in .local/share/applications and .config/autostart/
3. then yourvpn is available via your applications and autostart as a startup application
