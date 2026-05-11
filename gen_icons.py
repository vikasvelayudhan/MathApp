#!/usr/bin/env python3
"""Generate simple PNG icons for the PWA."""
import struct, zlib, math

def make_png(size):
    # Draw a gradient background with a rocket emoji-style graphic
    px = []
    cx, cy = size/2, size/2
    r = size/2
    for y in range(size):
        row = []
        for x in range(size):
            # Rounded rect mask
            bx = abs(x - cx) - (r - r*0.18)
            by_ = abs(y - cy) - (r - r*0.18)
            corner = r * 0.18
            dist = math.sqrt(max(0,bx)**2 + max(0,by_)**2)
            in_shape = dist <= corner

            if not in_shape:
                row += [0, 0, 0, 0]
                continue

            # Background gradient: deep purple to cyan
            t = (x + y) / (size * 2)
            rr = int(13 + t * (30 - 13))
            gg = int(13 + t * (100 - 13))
            bb = int(26 + t * (200 - 26))

            # Draw a simple rocket shape
            nx = (x - cx) / r
            ny = (y - cy) / r
            # body
            in_body = (abs(nx) < 0.18 and -0.45 < ny < 0.30)
            # nose
            in_nose = (abs(nx) < 0.18 - (ny + 0.45) * 0.3 and -0.70 < ny < -0.45)
            # fins
            in_fin = (0.18 < abs(nx) < 0.38 and 0.15 < ny < 0.45 and abs(nx) - 0.18 < (0.45 - ny) * 0.7)
            # flame
            in_flame = (abs(nx) < 0.10 and 0.30 < ny < 0.55 and abs(nx) < (0.55 - ny) * 0.5)
            # window
            in_window = ((nx**2 + (ny+0.05)**2) < 0.025)

            if in_window:
                row += [6, 182, 212, 255]
            elif in_nose or in_body or in_fin:
                row += [230, 220, 255, 255]
            elif in_flame:
                flame_t = (ny - 0.30) / 0.25
                fr = int(245 + flame_t * 10)
                fg = int(158 - flame_t * 100)
                fb = int(11)
                row += [min(255,fr), max(0,fg), fb, 255]
            else:
                row += [rr, gg, bb, 255]
        px.append(row)
    return encode_png(px, size)

def encode_png(pixels, size):
    def chunk(tag, data):
        c = zlib.crc32(tag + data) & 0xffffffff
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', c)

    raw = b''
    for row in pixels:
        raw += b'\x00' + bytes(row)
    compressed = zlib.compress(raw, 9)

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)
    ihdr = chunk(b'IHDR', ihdr_data)
    idat = chunk(b'IDAT', compressed)
    iend = chunk(b'IEND', b'')
    return sig + ihdr + idat + iend

import os
base = '/Users/D068004/Desktop/MathApp/icons'
for sz, name in [(192, 'icon-192.png'), (512, 'icon-512.png')]:
    data = make_png(sz)
    with open(os.path.join(base, name), 'wb') as f:
        f.write(data)
    print(f'Generated {name} ({sz}x{sz})')
