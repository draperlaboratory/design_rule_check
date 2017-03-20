__author__ = 'mcorriere@draper.com'

import argparse as argp
import os, time

suffix = '_checked_'
timestamp = time.strftime("%Y%m%d_%H%M%S")

def writeOut(filename, directory):

    if directory[-1] != '/':
        directory = directory + '/'

    out_file = directory + filename.rstrip('.dxf') + suffix + timestamp

    dxf  = out_file + '.dxf'
    pdf  = out_file + '.pdf'
    json = out_file + '.json'

    dxf_out  = open(dxf, 'w+')
    pdf_out  = open(pdf, 'w+')
    json_out = open(json, 'w+')
    
    dxf_out.close()
    pdf_out.close()
    json_out.close()


def main():

    parser = argp.ArgumentParser()
    parser.add_argument('filename',
                        help='The .dxf file to process')
    parser.add_argument('in_dir',
                        help='The directory the file resides in')
    parser.add_argument('out_dir',
                        help='The directory where results will be written')
    args = parser.parse_args()

    filename = args.filename
    inputDirectory = args.in_dir
    outputDirectory = args.out_dir

    writeOut(filename, outputDirectory)

if __name__ == '__main__':
  main()
