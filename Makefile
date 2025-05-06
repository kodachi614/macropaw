# SPDX-FileCopyrightText: 2022 Kodachi 6 14
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2022 Kodachi 6 14
#
# This file is part of the MacroPaw firmware.
#
# The MacroPaw firmware is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or any
# later version.
#
# The MacroPaw firmware is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the MacroPaw firmware. If not, see <https://www.gnu.org/licenses/>.

# BOARDS is the set of all boards that can be built by the normal build
# process, defined by the board_rule macro below. If you add a new board, and
# it can be built like the other BOARDS, you'll need to add it to this list.
#
# If the new board needs a custom build process, DO NOT add it to this list.
# Instead add it to CUSTOM_BOARDS below, and add a custom target for it.

BOARDS=KnGXT KnGYT

# CUSTOM_BOARDS is the set of all boards that need a custom build
# process. See above.
CUSTOM_BOARDS=

all: $(BOARDS) $(CUSTOM_BOARDS)

# The MacroPaw firmware is built atop CircuitPython and KMK. This Makefile
# expects to find the built CircuitPython firmware in tools/base-firmware.uf2,
# and the KMK firmware tarfile in tools/kmk-tarfile.tgz. If you're developing,
# copy your development versions into place; if either is missing, it'll be
# fetched from www.kodachi.com.

KMK_DIR="../../kmk_firmware/kmk"
CIRCUITPYTHON_BASE_VERSION=8.1.0-gaf5ee803
KMK_VERSION=8913b23d5a72dc7bad84ba28be4cbe9d48031848

CIRCUITPYTHON_BASE_URL=https://www.kodachi.com/firmware/circuitpython-kodachi-$(CIRCUITPYTHON_BASE_VERSION)
KMK_URL=https://www.kodachi.com/firmware/kmk-$(KMK_VERSION).tgz

# $(call board_rule,board) generates the basic build targets for a given board,
# namely the targets for its base .uf2 file and its macropaw .uf2 file. The
# bare board name is an alias for the macropaw .uf2 file.
#
# We need to have per-board base firmware files because a CircuitPython build
# is specific to a given board.

define board_rule
macropaw-$1.uf2: tools/base-firmware-$1.uf2 tools/kmk-tarfile.tgz $(wildcard $1/firmware/*.py)
	@echo "\n== Building $$@..."
	bash tools/build-uf2 $1 $$$$(pwd) $(VOLNAME)

$1: macropaw-$1.uf2

tools/base-firmware-$1.uf2:
	curl --fail -L $(CIRCUITPYTHON_BASE_URL)-$1.uf2 -o $$@
endef

# We'll use BOARDS to generate basic targets for all of our boards.
# If you add a new board that can't use this target, you'll need to
# NOT add it to BOARDS, and instead add a custom target for it.

$(foreach board,$(BOARDS),$(eval $(call board_rule,$(board))))

# We need tools/base-firmware.uf2 and tools/kmk-tarfile.tgz for
# dependent things. If these are missing, fetch them from the 'Net.

tools/kmk-tarfile.tgz:
	curl --fail -L $(KMK_URL) -o $@

clean: FORCE
	rm -f $(addsuffix .uf2, $(addprefix macropaw-, $(BOARDS)))

clobber: clean FORCE
	rm -f $(addsuffix .uf2, $(addprefix tools/base-firmware-, $(BOARDS)))
	rm -f tools/kmk-tarfile.tgz

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
