#!/usr/bin/python

import argparse, glob, os
from PIL import Image

formats = ["BMP", "DIB", "EPS", "GIF", "ICNS", "ICO", "IM", "JPG", "JPEG",
           "J2K", "J2P", "JPX", "MSP", "PCX", "PNG", "PPM", "SGI",
           "SPIDER", "TGA", "TIFF", "WebP", "XBM"]
parser = argparse.ArgumentParser(description="Pillow example - batch converter.")
os.makedirs("converted_images", exist_ok=True)
parser.add_argument('--outdir', default='./converted_images', help='Directory to save converted image files')
parser.add_argument('--outformat', choices=formats, default="JPG",
                    help='Output image format required. The output file will be written with the same base-name as the input file, but with an extension reflecting the format')
parser.add_argument('--indir', default="./images")
args = parser.parse_args()

infiles = []
for name in os.listdir(args.indir):
    infiles.append(os.path.join(args.indir, name))

for fname in infiles:
    if os.path.isdir(fname): continue
    base = os.path.basename(fname)
    f, ext = os.path.splitext(base)
    if len(ext) <= 1: continue
    ext = ext[1:]
    if ext.upper() not in formats:
        print('{}: format not supported .. ignoring'.format(fname))
        continue
    image = Image.open(fname)
    opath = os.path.join(args.outdir, '{}.{}'.format(f, args.outformat.lower()))
    image.save(opath)