"""Generate web-sized gallery thumbnails.

The gallery grid shows every photo in a 300px-tall cover-cropped tile, so it has
no use for the multi-megabyte originals. This builds a WebP + JPEG derivative of
each original at THUMB_MAX_PX; the full-resolution file is still what the
lightbox opens.

Re-run after adding photos to static/images/gallery/:

    .venv/Scripts/python.exe tools/make_thumbs.py

Pillow is only needed to run this script -- it is not a runtime dependency, and
the generated thumbnails are committed alongside the originals.
"""

import json
import os

from PIL import Image, ImageOps

SRC_ROOT = os.path.join('static', 'images', 'gallery')
OUT_ROOT = os.path.join('static', 'images', 'gallery-thumbs')
MANIFEST = os.path.join(OUT_ROOT, 'manifest.json')
CATEGORIES = ['kitchens', 'bathrooms', 'decks', 'doors', 'custom']
EXTENSIONS = ('.jpg', '.jpeg', '.png')

THUMB_MAX_PX = 800   # covers the widest tile (~570px) at 2x device pixel ratio
JPEG_QUALITY = 82
WEBP_QUALITY = 78

# Standalone page images, sized to roughly 2x the box they actually render in.
# Written to static/images/optimized/ so the originals are never overwritten.
OPT_ROOT = os.path.join('static', 'images', 'optimized')
PAGE_IMAGES = [
    ('projects/slider/gallerySlide1.jpg', 1600),  # slider caps at 800px wide
    ('projects/slider/gallerySlide2.jpg', 1600),
    ('projects/slider/gallerySlide3.jpg', 1600),
    ('owner-photo.jpg', 800),                     # renders in a ~200px-tall box
    ('projects/hero-background.jpg', 1920),       # full-bleed CSS background
]


def build(force=False):
    saved_before = saved_after = count = skipped = 0
    manifest = {}

    for category in CATEGORIES:
        src_dir = os.path.join(SRC_ROOT, category)
        out_dir = os.path.join(OUT_ROOT, category)
        if not os.path.isdir(src_dir):
            continue
        os.makedirs(out_dir, exist_ok=True)

        for filename in sorted(os.listdir(src_dir)):
            if not filename.lower().endswith(EXTENSIONS):
                continue

            src = os.path.join(src_dir, filename)
            stem = os.path.splitext(filename)[0]
            jpg_out = os.path.join(out_dir, stem + '.jpg')
            webp_out = os.path.join(out_dir, stem + '.webp')

            # Skip work when both derivatives are newer than the original.
            if not force and os.path.exists(jpg_out) and os.path.exists(webp_out):
                src_mtime = os.path.getmtime(src)
                if (os.path.getmtime(jpg_out) > src_mtime
                        and os.path.getmtime(webp_out) > src_mtime):
                    with Image.open(jpg_out) as done:
                        manifest['%s/%s' % (category, filename)] = done.size
                    skipped += 1
                    continue

            with Image.open(src) as im:
                # Honour camera rotation now, so the tile matches the lightbox.
                im = ImageOps.exif_transpose(im)
                im = im.convert('RGB')
                im.thumbnail((THUMB_MAX_PX, THUMB_MAX_PX), Image.LANCZOS)
                im.save(jpg_out, 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True)
                im.save(webp_out, 'WEBP', quality=WEBP_QUALITY, method=6)
                manifest['%s/%s' % (category, filename)] = im.size

            saved_before += os.path.getsize(src)
            saved_after += os.path.getsize(webp_out)
            count += 1

    with open(MANIFEST, 'w') as fh:
        json.dump(manifest, fh, indent=0, sort_keys=True)

    mb = 1024 * 1024
    print('generated %d thumbnails (%d already current)' % (count, skipped))
    if count:
        print('originals %.1f MB -> webp thumbs %.1f MB (%.0f%% smaller)'
              % (saved_before / mb, saved_after / mb,
                 100 * (1 - saved_after / saved_before)))


def build_page_images(force=False):
    """Shrink the handful of fixed page images that are served far oversized."""
    before = after = count = 0

    for rel, max_px in PAGE_IMAGES:
        src = os.path.join('static', 'images', *rel.split('/'))
        if not os.path.exists(src):
            print('  missing, skipped: %s' % rel)
            continue

        stem = os.path.splitext(rel)[0]
        jpg_out = os.path.join(OPT_ROOT, *(stem + '.jpg').split('/'))
        webp_out = os.path.join(OPT_ROOT, *(stem + '.webp').split('/'))
        os.makedirs(os.path.dirname(jpg_out), exist_ok=True)

        if not force and os.path.exists(jpg_out) and os.path.exists(webp_out):
            src_mtime = os.path.getmtime(src)
            if (os.path.getmtime(jpg_out) > src_mtime
                    and os.path.getmtime(webp_out) > src_mtime):
                continue

        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert('RGB')
            im.thumbnail((max_px, max_px), Image.LANCZOS)
            im.save(jpg_out, 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True)
            im.save(webp_out, 'WEBP', quality=WEBP_QUALITY, method=6)

        before += os.path.getsize(src)
        after += os.path.getsize(webp_out)
        count += 1

    mb = 1024 * 1024
    if count:
        print('optimised %d page images: %.1f MB -> %.1f MB webp (%.0f%% smaller)'
              % (count, before / mb, after / mb, 100 * (1 - after / before)))


if __name__ == '__main__':
    build()
    build_page_images()
