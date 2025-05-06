#!/bin/sh

BOARDID="$1"

wait_boot_volume() {
    local echoed=
    local tries=60

    while [ ! -d /Volumes/RPI-RP2 ]; do
        if [ -z "$echoed" ]; then
            echo "Waiting for MacroPaw to reappear in boot mode..."
            echoed=1
        fi

        tries=$(( $tries - 1 ))

        if [ $tries -eq 0 ]; then
            echo "MacroPaw did not reappear in boot mode" >&2
            exit 1
        fi

        # echo "...not there ($tries)"

        sleep 1
    done

    echo "...connected"
}

wait_no_boot_volume() {
    echoed=
    tries=60

    while [ -r /Volumes/RPI-RP2 ]; do
        if [ -z "$echoed" ]; then
            echo "Waiting for MacroPaw to disconnect after erasure..."
            echoed=1
        fi

        tries=$(( $tries - 1 ))

        if [ $tries -eq 0 ]; then
            echo "MacroPaw did not disconnect after erasure" >&2
            exit 1
        fi

        # echo "...still there ($tries)"

        sleep 1
    done

    echo "...disconnected"
}

if [ -z "$BOARDID" ]; then
    echo "Usage: $0 <boardID>" >&2
    exit 1
fi

if [ ! -f macropaw-$BOARDID.uf2 ]; then
    echo "No UF2 file for board $BOARDID found" >&2
    exit 1
fi

if [ ! -d /Volumes/RPI-RP2 ]; then
    echo "No MacroPaw in boot mode found" >&2
    exit 1
fi

echo "Erasing MacroPaw..."

if ! time cp tools/flash_nuke.uf2 /Volumes/RPI-RP2; then
    echo "Failed to erase MacroPaw" >&2
    diskutil eject /Volumes/RPI-RP2 >/dev/null 2>&1
    exit 1
fi

diskutil eject /Volumes/RPI-RP2 >/dev/null 2>&1

wait_no_boot_volume
wait_boot_volume
sleep 1

echo "Flashing MacroPaw..."

if ! time cp macropaw-$BOARDID.uf2 /Volumes/RPI-RP2; then
    echo "Failed to flash MacroPaw" >&2
    diskutil eject /Volumes/RPI-RP2 >/dev/null 2>&1
    exit 1
fi

diskutil eject /Volumes/RPI-RP2 >/dev/null 2>&1

wait_no_boot_volume


