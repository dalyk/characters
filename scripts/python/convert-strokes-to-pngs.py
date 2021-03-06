#!/usr/bin/python
import argparse
from htmlcanvas import convert_all_strokes_to_images

parser = argparse.ArgumentParser(description='Convert stokes to png files')
parser.add_argument('--input', '-i', metavar='indirs', nargs='+', dest='src',
                    default='.',
                    help='the directories in which to convert strokes (default: .)')
parser.add_argument('--output', '-o', metavar='outdirs', nargs='+', dest='dest',
                    default='.',
                    help='the directories in which to place the new images (default: .)')
parser.add_argument('--thickness', '--linewidth', dest='line_width',
                    type=float, default=0.01,
                    help='the thickness of the line in the new images')
parser.add_argument('--scale', '-s', dest='scale_factor',
                    type=float, default=1,
                    help='how much to scale the original strokes')
##parser.add_argument('--filetype', '--type', dest='file_ext', default='png',
##                   help='the type of image to save the strokes in (default: png)')

if __name__ == '__main__':
    args = parser.parse_args()
##    args.file_ext = '.' + args.file_ext.strip('.')
    convert_all_strokes_to_images(src=args.src, dest=args.dest, line_width=args.line_width, scale_factor=args.scale_factor)#, new_ext=args.file_ext)
