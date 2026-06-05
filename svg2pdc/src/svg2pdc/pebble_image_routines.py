# SPDX-FileCopyrightText: 2024 Google LLC
# SPDX-License-Identifier: Apache-2.0
#
# Color-conversion subset of the Pebble SDK's pebble_image_routines.py, vendored
# so svg2pdc can run standalone under Python 3 + uv. Function names keep the
# `pebble_*` prefix the original svg2pdc.py expects (the SDK has since renamed
# them to `*_pebble64_palette`).
#
# pebble64 = the 2-bits-per-channel palette available on color Pebbles.


def pebble_nearest_color_to_pebble_palette(r, g, b, a):
    """Match an rgba32 pixel to the nearest color in the 2-bit Pebble palette."""
    a = ((a + 42) // 85) * 85  # nearest alpha for 2-bit range
    # clear fully transparent pixels
    if a == 0:
        r, g, b = (0, 0, 0)
    else:
        r = ((r + 42) // 85) * 85
        g = ((g + 42) // 85) * 85
        b = ((b + 42) // 85) * 85
    return r, g, b, a


def pebble_truncate_color_to_pebble_palette(r, g, b, a):
    """Truncate an rgba32 pixel to the next-lower color in the 2-bit Pebble palette."""
    a = (a // 85) * 85
    if a == 0:
        r, g, b = (0, 0, 0)
    else:
        r = (r // 85) * 85
        g = (g // 85) * 85
        b = (b // 85) * 85
    return r, g, b, a


def rgba32_triplet_to_argb8(r, g, b, a):
    """Pack a 32-bit RGBA color into a single ARGB8 byte (2 bits per channel)."""
    a, r, g, b = (a >> 6, r >> 6, g >> 6, b >> 6)
    return (a << 6) | (r << 4) | (g << 2) | b
