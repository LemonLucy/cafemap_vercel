#!/usr/bin/env python3
from PIL import Image

sizes = [
    ('icon-192.png', 192),
    ('icon-512.png', 512),
    ('apple-touch-icon.png', 180),
    ('maskable-icon.png', 512)
]

img = Image.open('home.png')
for filename, size in sizes:
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(filename, 'PNG', optimize=True)
    print(f'Created {filename} ({size}x{size})')
