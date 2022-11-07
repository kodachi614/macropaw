#!/bin/bash

# This is meant to run on a Linux box to set up a base FAT image for
# us to use for firmware. Here's the trivial way to use it:
#
# docker run --privileged=true --rm -v $(pwd):/export ubuntu bash /export/linux-init-fat.sh

set -ex

apt-get update
apt-get install -y fdisk dosfstools file

if losetup -a | grep -q /export/base-fat.img; then
    if mount | grep -q /dev/loop0; then
        umount /dev/loop0
    fi

    losetup -d /dev/loop0
fi

rm -f /export/base-fat.img
dd if=/dev/zero of=/export/base-fat.img bs=1M count=8

mkfs.vfat -n "MACROPAW" -m - /export/base-fat.img <<EOF
This is not a bootable disk; it contains firmware for the
Kodachi 6 14 MacroPaw KnGXT. Please don't try to boot it.
EOF

losetup -fP /export/base-fat.img
mount /dev/loop0 /mnt
touch /mnt/.metadata_never_index
touch /mnt/.Trashes
mkdir /mnt/.fseventsd
touch /mnt/.fseventsd/no_log
mkdir /mnt/lib
echo 'print("Hello from Linux FAT\n")' > /mnt/code.py
sync
umount /mnt
losetup -d /dev/loop0
