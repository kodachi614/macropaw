all: KnGXT/firmware.uf2

KMK_DIR="../../kmk_firmware/kmk"
CIRCUITPYTHON_FIRMWARE="$(PWD)/../circuitpython/ports/raspberrypi/build-kodachi_macropaw_kngxt/firmware.uf2"

# KnGXT/firmware.uf2: \
# 	tools/base-fat.img \
# 	$(glob $(KMK_DIR)/*) \
# 	$(CIRCUITPYTHON_FIRMWARE) \
# 	$(glob KnGXT/firmware/*.py)

KnGXT/firmware.uf2: \
	tools/base-fat.img \
	$(wildcard KnGXT/firmware/*.py)
	sh tools/build-uf2

tools/base-fat.img:
	cd tools && \
	docker run --privileged=true --rm -v $$(pwd):/export ubuntu bash /export/linux-init-fat.sh

clean: FORCE
	rm -f tools/base-fat.img
	rm -f tools/macropaw.img

clobber: clean FORCE
	rm -f KnGXT/firmware.uf2

# Sometimes we have a file-target that we want Make to always try to
# re-generate (such as compiling a Go program; we would like to let
# `go install` decide whether it is up-to-date or not, rather than
# trying to teach Make how to do that).  We could mark it as .PHONY,
# but that tells Make that "this isn't a real file that I expect to
# ever exist", which has a several implications for Make, most of
# which we don't want.  Instead, we can have them *depend* on a .PHONY
# target (which we'll name "FORCE"), so that they are always
# considered out-of-date by Make, but without being .PHONY themselves.
.PHONY: FORCE