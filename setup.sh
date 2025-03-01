#!/bin/bash

read -r -p "Enter path to your vpn config file:" config_path
read -r -p "Give this vpn a name:" vpn_name

sudo apt install gir1.2-appindicator3-0.1
sudo /usr/bin/python3 -m pip install psutil

FILE1=/etc/openvpn/"$vpn_name".conf
echo "creating $FILE1"
if [[ -f "$FILE1" ]];
then
    echo "$FILE1  already exists."
else
    sudo cp "$config_path" /etc/openvpn/"$vpn_name".conf
fi

FILE2=~/.local/share/applications/"$vpn_name".desktop
FILE3=~/.config/autostart/"$vpn_name".desktop

echo "creating $FILE2 and $FILE3"
project_dir=$(pwd)

if [[ -f "$FILE3" ]];
then
  echo "$FILE3 already exists"
else
  sed -e "s+<PROJECT_DIR>+$project_dir+g"  -e "s+<VPN>+$vpn_name+g" vpn.desktop.template > "$vpn_name".desktop
  cp "$project_dir"/"$vpn_name".desktop ~/.local/share/applications/
  cp "$project_dir"/"$vpn_name".desktop ~/.config/autostart/
  rm "$project_dir"/"$vpn_name".desktop
fi

echo """
append these lines to your /etc/sudoers  file
<------------------------------------------------------------------>
ALL ALL=NOPASSWD: /bin/systemctl start openvpn@$vpn_name.service
ALL ALL=NOPASSWD: /bin/systemctl stop openvpn@$vpn_name.service
ALL ALL=NOPASSWD: /bin/systemctl restart openvpn@$vpn_name.service
<------------------------------------------------------------------>
"""

echo "generating removal script uninstall.sh for future cleanup"
echo """#!/bin/bash
rm ~/.local/share/applications/$vpn_name.desktop
rm ~/.config/autostart/$vpn_name.desktop
rm /etc/openvpn/$vpn_name.conf

sudo apt uninstall gir1.2-appindicator3-0.1
sudo /usr/bin/python3 -m pip uninstall psutil

echo 'remove these lines from your /etc/sudoers  file if you added them
<------------------------------------------------------------------>
ALL ALL=NOPASSWD: /bin/systemctl start openvpn@$vpn_name.service
ALL ALL=NOPASSWD: /bin/systemctl stop openvpn@$vpn_name.service
ALL ALL=NOPASSWD: /bin/systemctl restart openvpn@$vpn_name.service
<------------------------------------------------------------------>'

""" >> uninstall.sh

chmod +x uninstall.sh
