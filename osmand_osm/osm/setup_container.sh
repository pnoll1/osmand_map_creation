#! /bin/sh
# unprivleged setup
# must work with values in /etc/subuid and /etc/subgid
# in /etc/lxc/default.conf add 
# lxc.idmap = u 0 231072 65536 
# lxc.idmap = g 0 232072 65536
# if using btrfs backin add --bdev btrfs before --
# setup container
sudo lxc-create -q osmand_map_creation -t download -- -d debian -r bookworm -a amd64
sudo lxc-start osmand_map_creation
sudo cp setup_app.sh /var/lib/lxc/osmand_map_creation/rootfs/
