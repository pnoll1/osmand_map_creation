#! /bin/sh
#set container name
container=omc
sudo apt-get install -y incus
incus launch images:debian/12 $container
incus exec $container -- bash -s < setup_app.sh
