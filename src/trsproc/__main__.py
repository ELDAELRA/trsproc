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
from trsproc import parser

console = Console()
FLAGS = {
    '-cne':("deletes the Named Entity annotations if any are present in the input TRS.", "Cleaning NE annotation from TRS in", "trs", "parser.TRSParser.cleanNEfromTRS"),
    '-crt':("Correction de TRS selon problèmes rencontrées", "TRS custom correction in", "trs", "None"),
    '-ne':("extracts the Named Entity annotations if any are present in the input TRS and put them in a tabular file.", "NE extraction from", "trs", "parser.TRSParser.retrieveNEToTsv"),
    '-pne':("pre-annotates the input TRS using the table created in the `-ne` flag as a custom annotation dictionnary.", "NE pre-annotation for TRS in", "trs", "utils.trsPreannotation"),
    '-prt':("print the parsed TRS contents directly in the console.", "Printing TRS contents", "trs", "parser.TRSParser.print"),
    '-rpt':("performs the operations of the `-tmp` and `-vsi` flags in order to obtain the basic elements for data validation. An additional report is produced with pause segments longer than 0.5s and speech segments shorter than 10s.", "Creating validation report for target Section", "trs", "utils.tmpReport"),
    '-rs':("calculates the minimum sample needed for the validation of the input TRS transcription and the extracts random segments (audio and text, the latter in a tabular file) according to a given quantity.", "Extracting random segments from", "trs", "utils.randomSampling"),
    '-rsne':("calculates the minimum sample needed for the validation of Named Entities of the input TRS and extracts them (audio segments and text, the latter in a tabular file) randomly by a given amount.", "Extracting random NE from", "trs", "utils.randomSamplingNE"),
    '-tg':("converts TRS files to TextGrid files.", "Converting to TextGrid in", "trs", "parser.TRSParser.trsToTextGrid"),
    '-tgrs':("converts TextGrid files to TRS files.", "Converting TextGrid to TRS in", "TextGrid", "parser.TRSParser.textGridToTRS"),
    '-tmp':("creates TRS-temporary files in a directory named \"tmp\". By default, these files contain only the target section(s) of the original TRS.", "Writing temporary TRS in", "trs", "parser.TRSParser.trsTMP"),
    '-trs':("rewrites a TRS file using the input txt file and a TRS-placeholder placed in a subfolder of the parent input folder. The rewritten TRS will have the content of the txt and the structure of the TRS-placeholder.", "Re-writing TRS in", "txt", "parser.TRSParser.txtToTrs"),
    '-tsv':("produces a tabular file with the structures and contents of the TRS files.", "Writing tsv from TRS in", "trs", "parser.TRSParser.trsToTsv"),
    '-txt':("creates txt and TRS-placeholder files. The first only containing the transcription of the original TRS, the latter having its XML structure.", "Extracting txt and TRS-placeholder in", "trs", "parser.TRSParser.trsToTxt"),
    '-vad':("converts TextGrid files resulting from the use of a voice activity detection algorithm (VAD) into TRS files.", "Converting TextGrid-VAD in", "TextGrid", "parser.TRSParser.vadToTRS"),
    '-vsi':("produces a tabular file containing basic lexical information and statistics concerning the input TRS.", "Extracting TRS statistics in", "trs", "parser.TRSParser.validateTRS")
}

CORRECTIONS = {
    1:("turnDifferenceTRS", "search for differences in segmentation for the input TRS and its twin placed in a subfolder named \"twin\".", "utils.turnDifferenceTRS"),
    2:("trsEmptySpaceBeforeNE", "adds an empty space before each NE annotation and save the new TRS in a separate subfolder", "utils.trsEmptySpaceBeforeNE"),
    3:("correctionLà", "corrects sentences ending with là in la. This needs the execution of -txt flag beforehand.", "utils.correctionLà"),
    4:("correctionMaj", "corrects misplaced capiral letters.", "utils.correctionMaj")
}

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

        procParam = FLAGS[p]
        docus = sorted(glob.glob(os.path.join(docPath, f'*.{procParam[2]}')))
        docus = list(set(docus))
        if p in ['-rs', '-rsne']:
            exec(f"{procParam[-1]}(docus, docPath)")
        else:
            if p == '-crt':
                for c in CORRECTIONS:
                    print(f"{c} -> {CORRECTIONS[c][0]}, {CORRECTIONS[c][1]}")
                funChoice = int(input("Insert the desired correction function number (list above)\t"))
                fun = CORRECTIONS[funChoice][-1]
            with console.status(f"{procParam[1]} {docPath} with {len(docus)} files", spinner='point') as status:
                for d in docus:
                    if procParam[2] == 'trs':
                        ff = parser.TRSParser(d, audioFormat, langT)
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
        for p in FLAGS:
            print(f"{p} -> {FLAGS[p][0]}")

    print("--- %s sec taken ---" % round((time.time() - start_time), 2))

if __name__ == '__main__':
    main()    