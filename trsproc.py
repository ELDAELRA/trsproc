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
from parsing_trs import TRSParser
import utils_trsproc

console = Console()

dicoPhases = {
	'-cne':("deletes the Named Entity annotations if any are present in the input TRS.", "Cleaning NE annotation from TRS in", 'trs', TRSParser.cleanNEfromTRS),
	'-crt':("Correction de TRS selon problèmes rencontrées", "TRS custom correction in", 'trs', None),
	'-ne':("extracts the Named Entity annotations if any are present in the input TRS and put them in a tabular file.", "NE extraction from", 'trs', TRSParser.retrieveNEToTsv),
	'-pne':("pre-annotates the input TRS using the table created in the `-ne` flag as a custom annotation dictionnary.", "NE pre-annotation for TRS in", 'trs', utils_trsproc.trsPreannotation),
	'-rpt':("performs the operations of the `-tmp` and `-vsi` flags in order to obtain the basic elements for data validation.", "Creating validation report for target Section", 'trs', utils_trsproc.soge6ptsReport),
	'-rs':("calculates the minimum sample needed for the validation of the input TRS transcription and the extracts random segments (~~audio~~ and text, the latter in a tabular file) according to a given quantity.", "Extracting random segments from", 'trs', utils_trsproc.randomSampling),
	'-rsne':("calculates the minimum sample needed for the validation of Named Entities of the input TRS and extracts them (~~audio segments~~ and text, the latter in a tabular file) randomly by a given amount.", "Extracting random NE from", 'trs', utils_trsproc.randomSamplingNE),
	'-tg':("converts TRS files to TextGrid files.", "Converting to TextGrid in", 'trs', TRSParser.trsToTextGrid),
	'-tgrs':("converts TextGrid files to TRS files.", "Converting TextGrid to TRS in", 'TextGrid', TRSParser.textGridToTRS),
	'-tmp':("creates TRS-temporary files in a directory named 'tmp'. By default, these files contain only the target section(s) of the original TRS.", "Writing temporary TRS in", 'trs', TRSParser.trsTMP),
	'-trs':("rewrites a TRS file using the input txt file and a TRS-placeholder placed in a subfolder of the parent input folder. The rewritten TRS will have the content of the txt and the structure of the TRS-placeholder.", "Re-writing TRS in", 'txt', TRSParser.txtToTrs),
	'-tsv':("produces a tabular file with the structures and contents of the TRS files.", "Writing tsv from TRS in", 'trs', TRSParser.trsToTsv),
	'-txt':("creates txt and TRS-placeholder files. The first only containing the transcription of the original TRS, the latter having its XML structure.", "Extracting txt and TRS-placeholder in", 'trs', TRSParser.trsToTxt),
	'-vad':("converts TextGrid files resulting from the use of a voice activity detection algorithm (VAD) into TRS files.", "Converting TextGrid in", 'TextGrid', TRSParser.vadToTRS),
	'-vsi':("produces a tabular file containing basic lexical information and statistics concerning the input TRS.", "Extracting TRS statistics in", 'trs', TRSParser.validateTRS)
}
possible_corrections = {
	'turnDifferenceTRS':"",
	'trsFinalCorrection':"",
	'correctionLà':"",
	'correctionMaj':""
}

#----------
def main():
	start_time = time.time()
	p = sys.argv[1]
	parser = argparse.ArgumentParser()
	parser.add_argument('-a', '--audio', required=False)
	parser.add_argument('-f', '--folder', required=False)
	parser.add_argument('-jkz', required=False, nargs='?')
	parser.add_argument('-plh', required=False, nargs='?')
	parser.add_argument('-s', '--section', required=False)
	args = parser.parse_args()

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

		procParam = dicoPhases[p]
		docus = sorted(glob.glob(os.path.join(docPath, f'*.{procParam[2]}')))
		docus = list(set(docus))
		fun = procParam[-1]
		if p in ['-rs', '-rsne']:
			fun(docus, docPath)
		else:
			if p == '-crt':
				for c in possible_corrections:
					print(f"{c} -> {possible_corrections[c]}")
				fun = input("Insert the desired correction function (list above)\t")
			with console.status(f"{procParam[1]} {docPath} with {len(docus)} files", spinner='point') as status:
				for d in docus:
					if procParam[2] == 'trs':
						ff = TRSParser(d, audioFormat, langT)
						if args.section:
							fun(ff, section_type=args.section)
						elif args.plh:
							fun(ff, False)
						else:
							fun(ff)
					else:
						fun(d)
			console.print(status)
	except (IndexError, KeyError):
		utils_trsproc.warningArgs(dicoPhases)

	print("--- %s sec taken ---" % round((time.time() - start_time), 2))

if __name__ == '__main__':
	main()	