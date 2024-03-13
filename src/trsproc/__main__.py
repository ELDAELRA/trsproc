# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
##
### ELDA-R&D-2023
#### Gabriele CHIGNOLI
#####

# Global imports
import glob, os, time
import argparse
from rich.console import Console

# Custom imports
import trsproc
from trsproc import parser, utils

console = Console()
FLAGS = {
    'cne':(
        "deletes the Named Entity annotations if any are present in the input TRS.",
        "Cleaning NE annotation from TRS in",
        'trs',
        'parser.TRSParser.cleanNEfromTRS'),
    'crt':(
        "Correction de TRS selon problèmes rencontrées",
        "TRS custom correction in",
        'trs',
        'None'),
    'lang':(
        "adds a language tag to each transcription segment not having one in the input TRS. It also modifies the actual language tags using the provided language dictionary in JSON format named \"lang-tag.json\" in the same input folder.",
        "Adding language tags to",
        'trs',
        'utils.addLangTag'),
    'ne':(
        "extracts the Named Entity annotations if any are present in the input TRS and put them in a tabular file.",
        "NE extraction from",
        'trs',
        'parser.TRSParser.retrieveNEToTsv'),
    'pne':(
        "pre-annotates the input TRS using the table created in the `-ne` flag as a custom annotation dictionnary.",
        "NE pre-annotation for TRS in",
        'trs',
        'utils.trsPreannotation'),
    'prt':(
        "print the parsed TRS contents directly in the console.",
        "Printing TRS contents",
        'trs',
        'parser.TRSParser.print'),
    'rpt':(
        "performs the operations of the `-tmp` and `-vsi` flags in order to obtain the basic elements for data validation. An additional report is produced with pause segments longer than 0.5s and speech segments shorter than 10s.",
        "Creating validation report for target Section",
        'trs',
        'utils.tmpReport'),
    'rs':(
        "calculates the minimum sample needed for the validation of the input TRS transcription and the extracts random segments (audio and text, the latter in a tabular file) according to a given quantity.",
        "Extracting random segments from",
        'trs',
        'utils.randomSampling'),
    'rsne':(
        "calculates the minimum sample needed for the validation of Named Entities of the input TRS and extracts them (audio segments and text, the latter in a tabular file) randomly by a given amount.",
        "Extracting random NE from",
        'trs',
        'utils.randomSamplingNE'),
    'tg':(
        "converts TRS files to TextGrid files.",
        "Converting to TextGrid in",
        'trs',
        'parser.TRSParser.trsToTextGrid'),
    'tgrs':(
        "converts TextGrid files to TRS files.",
        "Converting TextGrid to TRS in",
        'TextGrid',
        'parser.TRSParser.textGridToTRS'),
    'tmp':(
        "creates TRS-temporary files in a directory named \"tmp\". By default, these files contain only the target section(s) of the original TRS.",
        "Writing temporary TRS in",
        'trs',
        'parser.TRSParser.trsTMP'),
    'trs':(
        "rewrites a TRS file using the input txt file and a TRS-placeholder placed in a subfolder of the parent input folder. The rewritten TRS will have the content of the txt and the structure of the TRS-placeholder.",
        "Re-writing TRS in",
        'txt',
        'parser.TRSParser.txtToTrs'),
    'tsv':(
        "produces a tabular file with the structures and contents of the TRS files.",
        "Writing tsv from TRS in",
        'trs',
        'parser.TRSParser.trsToTsv'),
    'txt':(
        "creates txt and TRS-placeholder files. The first only containing the transcription of the original TRS, the latter having its XML structure.",
        "Extracting txt (and TRS-placeholder) in",
        'trs',
        'parser.TRSParser.trsToTxt'),
    'vad':(
        "converts TextGrid files resulting from the use of a voice activity detection algorithm (VAD) into TRS files.",
        "Converting TextGrid-VAD in",
        'TextGrid',
        'parser.TRSParser.vadToTRS'),
    'vsi-lang':(
        "produces a tabular file containing basic information abouth the language tags present in the input TRS.",
        "Language summary from",
        'trs',
        'parser.TRSParser.summaryLangTRS'),
    'vsi':(
        "produces a tabular file containing basic lexical information and statistics concerning the input TRS.",
        "Extracting TRS statistics in",
        'trs',
        'parser.TRSParser.validateTRS')
}

CORRECTIONS = {
    1:('turnDifferenceTRS',
       "search for differences in segmentation for the input TRS and its twin placed in a subfolder named \"twin\".",
       'utils.turnDifferenceTRS'),
    2:('trsEmptySpaceBeforeNE',
       "adds an empty space before each NE annotation and save the new TRS in a separate subfolder",
       'utils.trsEmptySpaceBeforeNE'),
    3:('correctionLà',
       "corrects sentences ending with là in la. This needs the execution of -txt flag beforehand.",
       'utils.correctionLà'),
    4:('correctionMaj',
       "corrects misplaced capiral letters.",
       'utils.correctionMaj')
}

#----------
def main():
    start_time = time.time()

    argparser = argparse.ArgumentParser()
    argparser.add_argument('flag', nargs='?', default='helpmeobiwan', help="defines the processing to perform, in case of incorrect flag the list of possible ones and their function will be printed.\nGo to https://pypi.org/project/trsproc/ or https://github.com/ELDAELRA/trsproc for more information") # flag argument not explicited by - or --
    argparser.add_argument('-a', '--audio', default='wav', required=False, help="audio format corresponding to the input TRS if different from wav")
    argparser.add_argument('-cl', '--correctionlevel', required=False, help="correction levels established in lexicalproc (ELDA's internal script)")
    argparser.add_argument('-f', '--folder', default=os.getcwd(), required=False, help="target folder for processing if different from the current one.")
    argparser.add_argument('-jkz', '--japkorzh', required=False, action='store_true', help="specified if the language to be processed does not use ASCII/Latin characters")
    argparser.add_argument('-plh', '--placeholder', required=False, action='store_true', help="omits the creation of TRS-placeholder files")
    argparser.add_argument('-punct', '--punctuation', required=False, action='store_true', help="clear punctuation in the resulting txt file.")
    argparser.add_argument('-s', '--section', required=False, help="target section if different from \"report\"")
    argparser.add_argument('-t', '--tag', required=False, help="language to be added for the `lang` flag.")
    args = argparser.parse_args()

    try:
        if args.japkorzh:
            langT = 'jkz'
        else:
            langT = 'eu'

        f = args.flag
        procParam = FLAGS[f]
        docus = sorted(glob.glob(os.path.join(args.folder, f'*.{procParam[2]}')))
        docus = list(set(docus))

        if f in ['rs', 'rsne']:
            func = f"{procParam[-1]}(docus, {args.folder})"
            exec(func)
        else:
            if f == 'crt':
                for c in CORRECTIONS:
                    print(f"{c} -> {CORRECTIONS[c][0]}, {CORRECTIONS[c][1]}")
                funChoice = int(input("Insert the desired correction function number (list above)\t"))
                func = f"{CORRECTIONS[funChoice][-1]}(ff)"
            else:
                func = f"{procParam[-1]}(ff)"
            with console.status(f"{procParam[1]} {args.folder} with {len(docus)} files", spinner='point') as status:
                for d in docus:
                    if procParam[2] == 'trs':
                        ff = parser.TRSParser(d, args.audio, langT)
                        if args.section:
                            func = f"{procParam[-1]}(ff, section_type={args.section})"
                        elif args.placeholder:
                            if args.punctuation:
                                func = f"{procParam[-1]}(ff, need_placeholder=False, delete_punct=True)"
                            else:
                                func = f"{procParam[-1]}(ff, need_placeholder=False)"
                        elif args.correctionlevel:
                            func = f"{procParam[-1]}(ff, from_correction={args.correctionlevel})"
                        elif args.tag:
                            func = f"{procParam[-1]}(ff, {args.tag})"
                    else:
                        func = f"{procParam[-1]}(d)"
                    exec(func)
            console.print(status)
    except KeyError:
        print(f"Invalid flag, Please choose from the list below and call the program again:")
        for p in FLAGS:
            print(f"{p} -> {FLAGS[p][0]}")

    print("--- %s sec taken ---" % round((time.time() - start_time), 2))

if __name__ == '__main__':
    main()