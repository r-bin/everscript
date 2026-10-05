#!/usr/bin/env python3
"""
Throwaway verification script for docs/rom-extension-wishlist.md item 7
("More tiles / tile families").

Checks performed:
1. Compute the file-offset span implied by the "$D0..$DF = CHR tile graphics"
   claim in docs/rom-map-overview.md line 92, using this repo's own documented
   HiROM masking formula (file_offset = (bank & 0x3F) << 16 | addr), the same
   formula already used and cross-checked elsewhere in this repo (e.g.
   $9CC322 -> 0x1CC322, $91D000 -> 0x11D000, $EE0000 -> 0x2E0000).
2. Confirm the verified CHR master pointer table base ($EE0000, per
   docs/map_tile_graphics_decompression.md) does NOT fall inside that span,
   and instead sits in the file's near-tail region.
3. Spot-check the byte shape at $EE0000 (file 0x2E0000) to see whether it
   looks like a 3-byte-stride pointer table (as documented), as a sanity
   check independent of trusting the doc's prose.
4. Spot-check a sample of bytes from inside the nominal $D0..$DF span that
   ISN'T already accounted for by another known subsystem in
   docs/rom-map-overview.md's own file-offset table, to see whether it looks
   CHR/LZSS-shaped or not.

This is a static byte-pattern read of the raw ROM file only -- no live
emulator, no disassembler. Not proof of what the CPU executes, just evidence
about what bytes physically live where.
"""
import os

ROM_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "Secret of Evermore (U) [!].smc")


def file_offset(snes_bank: int, snes_addr: int) -> int:
    return ((snes_bank & 0x3F) << 16) | snes_addr


def main():
    rom = open(ROM_PATH, "rb").read()
    assert len(rom) == 3_145_728, f"unexpected ROM size {len(rom)}"

    # 1. $D0..$DF span
    lo = file_offset(0xD0, 0x0000)
    hi = file_offset(0xDF, 0xFFFF)
    print(f"$D0:0000..$DF:FFFF -> file offset 0x{lo:06X}..0x{hi:06X} "
          f"({hi - lo + 1} bytes)")

    # 2. Verified CHR master table base
    ee_off = file_offset(0xEE, 0x0000)
    print(f"$EE:0000 (verified CHR master pointer table base, per "
          f"map_tile_graphics_decompression.md) -> file offset 0x{ee_off:06X}")
    print(f"  Inside $D0..$DF span ({lo:06X}-{hi:06X})? "
          f"{lo <= ee_off <= hi}")

    # 3. Shape-check at $EE0000: read first 30 bytes as 10 x 3-byte LE pointers
    print("\nFirst 10 entries of the table at file 0x2E0000 (tile_id 0..9), "
          "as 3-byte little-endian pointers:")
    for tid in range(10):
        p = ee_off + tid * 3
        val = rom[p] | (rom[p + 1] << 8) | (rom[p + 2] << 16)
        print(f"  tile_id {tid:3d}: bytes {rom[p]:02X} {rom[p+1]:02X} {rom[p+2]:02X}"
              f"  -> 24-bit ptr 0x{val:06X}  (masked file offset 0x{val & 0x3FFFFF:06X})")

    # 4. Spot-check bytes inside $D0..$DF span, in the region NOT already
    #    claimed by another subsystem per docs/rom-map-overview.md's table
    #    (0x018000..0x11CFFF is flagged unknown-coarse; sample well inside it,
    #    away from any known boundary). file offset 0x180000 = file-bank-index
    #    0x18, which is within 0x10..0x1F (i.e. genuinely inside $D0..$DF).
    sample_off = 0x180000
    assert lo <= sample_off <= hi, "sample_off must be inside the $D0..$DF span"
    print(f"\n32 raw bytes at file 0x{sample_off:06X} "
          f"(inside $D0..$DF span, in the 0x128000..0x1BFFFF range "
          f"rom-map-overview.md already attributes to Script VM bytecode):")
    chunk = rom[sample_off:sample_off + 32]
    print("  " + " ".join(f"{b:02X}" for b in chunk))

    # 5. Scan a wide range of tile_ids' target banks to see whether ANY
    #    resolved CHR tile data address ever lands inside the $D0..$DF span.
    print("\nScanning tile_id 0..2999 target banks from the $EE0000 table:")
    bank_hist = {}
    n_scanned = 3000
    for tid in range(n_scanned):
        p = ee_off + tid * 3
        if p + 3 > len(rom):
            break
        val = rom[p] | (rom[p + 1] << 8) | (rom[p + 2] << 16)
        bank_byte = (val >> 16) & 0xFF
        bank_hist[bank_byte] = bank_hist.get(bank_byte, 0) + 1
    for bank_byte in sorted(bank_hist):
        masked_off = file_offset(bank_byte, 0x0000)
        in_span = lo <= masked_off <= hi
        print(f"  target bank ${bank_byte:02X}: {bank_hist[bank_byte]:4d} entries "
              f"-> masked file-bank-index 0x{(bank_byte & 0x3F):02X} "
              f"(inside $D0..$DF span? {in_span})")

    # Also confirm the already-known string table/dictionary chunk sits
    # inside the same nominal $D0..$DF span (cross-reference, not a new claim).
    str_lo = file_offset(0x91, 0xD000)
    str_hi = file_offset(0x91, 0xF32D)
    print(f"\nString Key Table (already verified in wishlist item 6): "
          f"file 0x{str_lo:06X}..0x{str_hi:06X}")
    print(f"  Inside $D0..$DF span? {lo <= str_lo <= hi and lo <= str_hi <= hi}")


if __name__ == "__main__":
    main()
