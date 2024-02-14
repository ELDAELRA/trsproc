# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
##
### ELDA-R&D-2023
#### Gabriele CHIGNOLI
#####
# USAGE
# python3 trsproc.py -flag [-option (folder)]

# Global imports
import glob, os, sys, time
import argparse
from rich.console import Console

# Custom imports
import trsproc
from trsproc import parser, utils

console = Console()

#----------
def main():
    start_time = time.time()
    p = sys.argv[1]
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-a', '--audio', required=False)
    argparser.add_argument('-f', '--folder', required=False)
    argparser.add_argument('-jkz', required=False, nargs='?')
    argparser.add_argument('-plh', required=False, nargs='?')
    argparser.add_argument('-s', '--section', required=False)
    argparser.add_argument('-cl', '--correctionlevel', required=False)
    args = argparser.parse_args(sys.argv[2:])

    try:
        if args.folder:
            docPath = args.folder
        else:
            docPath = os.getcwd()
        if args.audio:
            audioFormat = args.audio
        else:
            audioFormat = 'wav'
        if args.jkz:
            langT = 'jkz'
        else:
            langT = 'eu'

        procParam = trsproc.FLAGS[p]
        docus = sorted(glob.glob(os.path.join(docPath, f'*.{procParam[2]}')))
        docus = list(set(docus))
        if p in ['-rs', '-rsne']:
            exec(f"{procParam[-1]}(docus, docPath)")
        else:
            if p == '-crt':
                for c in trsproc.CORRECTIONS:
                    print(f"{c} -> {trsproc.CORRECTIONS[c][0]}, {trsproc.CORRECTIONS[c][1]}")
                funChoice = int(input("Insert the desired correction function number (list above)\t"))
                fun = trsproc.CORRECTIONS[funChoice][-1]
            with console.status(f"{procParam[1]} {docPath} with {len(docus)} files", spinner='point') as status:
                for d in docus:
                    if procParam[2] == 'trs':
                        ff = trsproc.parser.TRSParser(d, audioFormat, langT)
                        if args.section:
                            func = f"{procParam[-1]}(ff, section_type={args.section})"
                        elif args.plh:
                            func = f"{procParam[-1]}(ff, False)"
                        elif args.correctionlevel:
                            func = f"{procParam[-1]}(ff, from_correction={args.correctionlevel})"
                        else:
                            func = f"{procParam[-1]}(ff)"
                    else:
                        func = f"{procParam[-1]}(d)"
                    exec(func)
            console.print(status)
    except (IndexError, KeyError):
        print(f"Invalid flag, Please choose from the list below and call the program again:")
        for p in trsproc.FLAGS:
            print(f"{p} -> {trsproc.FLAGS[p][0]}")

    print("--- %s sec taken ---" % round((time.time() - start_time), 2))

if __name__ == '__main__':
    main()    