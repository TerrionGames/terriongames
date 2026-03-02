"""
Convert PNG images in each language folder under `images/` to JPG and rename
the first five images in each folder to `screen_01.jpg` ... `screen_05.jpg`.

Usage:
  python tools/convert_images.py [--images-dir images] [--remove-original] [--dry-run]

Options:
  --images-dir    Path to the images directory (default: images)
  --remove-original  Delete original PNG files after successful conversion
  --dry-run       Print actions without modifying files

Note: Requires Pillow. Install with `pip install pillow`.
"""

import argparse
from pathlib import Path
from PIL import Image


def convert_folder(folder: Path, remove_original: bool, dry_run: bool):
    png_files = sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == '.png'])
    if not png_files:
        return 0

    converted = 0
    for idx, p in enumerate(png_files):
        # Determine target name:
        # - first five files -> screen_01.jpg ... screen_05.jpg
        # - sixth file (index 5) -> banner.jpg
        # - remaining files -> same name with .jpg suffix
        if idx < 5:
            target = folder / f"screen_{idx+1:02}.jpg"
        elif idx == 5:
            target = folder / "banner.jpg"
        else:
            target = p.with_suffix('.jpg')

        if dry_run:
            print(f"DRY: {p} -> {target}")
            converted += 1
            continue

        try:
            with Image.open(p) as img:
                # Handle alpha by compositing over white background
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    rgba = img.convert('RGBA')
                    background = Image.new('RGB', rgba.size, (255, 255, 255))
                    background.paste(rgba, mask=rgba.split()[3])
                    rgb = background
                else:
                    rgb = img.convert('RGB')

                rgb.save(target, quality=95)

            if remove_original:
                try:
                    p.unlink()
                except Exception as e:
                    print(f"Warning: failed to remove original {p}: {e}")

            print(f"Converted: {p} -> {target}")
            converted += 1
        except Exception as e:
            print(f"Error converting {p}: {e}")

    return converted


def main():
    parser = argparse.ArgumentParser(description="Convert PNGs to JPG and rename screenshots per language folder.")
    parser.add_argument('--images-dir', default='images', help='Images directory (default: images)')
    parser.add_argument('--remove-original', action='store_true', help='Remove original PNG files after conversion')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without changing files')

    args = parser.parse_args()
    images_dir = Path(args.images_dir)
    if not images_dir.exists():
        print(f"Images directory not found: {images_dir}")
        return

    total = 0
    # Process language subfolders only (directories)
    for child in sorted(images_dir.iterdir()):
        if child.is_dir():
            print(f"Processing folder: {child}")
            converted = convert_folder(child, args.remove_original, args.dry_run)
            total += converted

    print(f"Done. Total images processed: {total}")


if __name__ == '__main__':
    main()
