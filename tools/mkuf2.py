import sys

import struct

UF2_MAGIC_START0 = 0x0A324655 # "UF2\n"
UF2_MAGIC_START1 = 0x9E5D5157 # Randomly selected
UF2_MAGIC_END    = 0x0AB16F30 # Ditto


PAGE_SIZE = 4096
BLOCK_SIZE = 256
BLOCKS_PER_PAGE = (PAGE_SIZE // BLOCK_SIZE)

class Block:
    def __init__(self, flags, addr, data):
        self.flags = flags
        self.addr = addr
        self.data = data


class Page:
    def __init__(self, baseaddr):
        self.blocks = [ None ] * BLOCKS_PER_PAGE
        self.baseaddr = baseaddr

    def add_block(self, block):
        page_offset = (block.addr - self.baseaddr) // BLOCK_SIZE

        self.blocks[page_offset] = block

    def all_zeroes(self):
        for i in range(BLOCKS_PER_PAGE):
            if self.blocks[i]:
                data = self.blocks[i].data

                if any(map(bool, data)):
                    return False
        
        return True

    def __iter__(self):
        for i in range(BLOCKS_PER_PAGE):
            if not self.blocks[i]:
                yield Block(0x2000, self.baseaddr + (i * BLOCK_SIZE), b"\x00" * BLOCK_SIZE)
            else:
                yield self.blocks[i]


class PageMap:
    def __init__(self):
        self.pages = {}

    def __len__(self):
        return len(self.pages.keys())

    def __iter__(self):
        for pkey in sorted(self.pages.keys()):
            yield self.pages[pkey]

    def add_block(self, block):
        page_base = (block.addr // PAGE_SIZE) * PAGE_SIZE
        pkey = "%08X" % page_base

        if not self.pages.get(pkey):
            self.pages[pkey] = Page(page_base)

        self.pages[pkey].add_block(block)


class UF2Reader:
    def __init__(self, path):
        self.path = path
        self.file = open(path, "rb")
        self.ptr = 0

    def __iter__(self):
        while True:
            rawblock = self.file.read(512)

            if not rawblock:
                break

            good = True

            (magic_start0, magic_start1, flags, addr,
             datalen, blkno, totalblks, family) = struct.unpack(b"<IIIIIIII", rawblock[0:32])

            magic_end = struct.unpack(b"<I", rawblock[508:512])[0]

            if (magic_start0 != UF2_MAGIC_START0) or (magic_start1 != UF2_MAGIC_START1):
                # sys.stderr.write("Skipping block at %08X: bad magic at start\n" % self.ptr)
                good = False

            if magic_end != UF2_MAGIC_END:
                # sys.stderr.write("Skipping block at %08X: bad magic at end\n" % self.ptr)
                good = False

            if good and (flags & 1):
                good = False

            if datalen > 476:
                assert False, "Invalid UF2 data size at %08X" % self.ptr

            self.ptr += 512

            if not good:
                continue

            yield Block(flags, addr, rawblock[32:32 + datalen])


class BinaryReader:
    def __init__(self, path, baseaddr):
        self.path = path
        self.file = open(path, "rb")
        self.ptr = baseaddr

    def __iter__(self):
        while True:
            rawblock = self.file.read(256)

            if not rawblock:
                return

            block = Block(0x2000, self.ptr, rawblock)
            self.ptr += len(rawblock)

            yield block


pagemap = PageMap()

for arg in sys.argv[1:]:
    if ":" in arg:
        addr, filename = arg.split(":", 1)
        addr = int(addr, 16)

        sys.stderr.write("@%08X -- %s\n" % (addr, filename))

        for block in BinaryReader(filename, addr):
            pagemap.add_block(block)
    else:
        sys.stderr.write("UF2 -- %s\n" % arg)

        for block in UF2Reader(arg):
            pagemap.add_block(block)

total_pages = 0
blocks_to_write = []

for page in pagemap:
    if not page.all_zeroes():
        total_pages += 1
        for block in page:
            blocks_to_write.append(block)

total_blocks = len(blocks_to_write)

if total_blocks != (total_pages * BLOCKS_PER_PAGE):
    errmsg = ("Internal error: should have %d blocks for %d pages but have %d" %
              (total_pages * BLOCKS_PER_PAGE, total_pages, total_blocks))

    assert False, errmsg

sys.stderr.write("Pages: %d\n" % total_pages)
sys.stderr.write("Blocks: %d\n" % total_blocks)

sequence_start = None
last_addr = None

datapadding = b""

while len(datapadding) < 512 - 256 - 32 - 4:
    datapadding += b"\x00\x00\x00\x00"

blockno = 0

for block in blocks_to_write:
    if sequence_start is None:
        sequence_start = block.addr
    else:
        if block.addr != wanted_addr:
            sys.stderr.write("%08X - %08X\n" % (sequence_start, wanted_addr))
            sequence_start = block.addr

    wanted_addr = block.addr + len(block.data)

    hd = struct.pack(b"<IIIIIIII",
        UF2_MAGIC_START0, UF2_MAGIC_START1,
        block.flags, block.addr, len(block.data), blockno, total_blocks, 0xE48BFF56)
    blockno += 1

    chunk = hd + block.data

    if len(block.data) != 256:
        chunk += b"\x00" * (256 - len(block.data))

    chunk += datapadding + struct.pack(b"<I", UF2_MAGIC_END)
    assert len(chunk) == 512

    sys.stdout.buffer.write(chunk)

if sequence_start != None:
    sys.stderr.write("%08X - %08X\n" % (sequence_start, wanted_addr))
