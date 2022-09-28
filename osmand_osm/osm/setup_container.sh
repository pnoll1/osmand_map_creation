#! /bin/sh

# setup container
sudo lxc-create -q osmand_map_creation -t download -- -d debian -r sid -a amd64
sudo lxc-start osmand_map_creation
sudo cp setup_app.sh /var/lib/lxc/osmand_map_creation/rootfs/
