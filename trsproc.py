# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
## ELDA-R&D-2023
### 30/01-20/12/2023
#### Gabriele CHIGNOLI
#####
# USAGE
# python3 trsproc.py -flag (folder)

"""
TODO
"""

# Global imports
import random
random.seed(42)
import glob, os, sys, time
from rich.console import Console

# Custom imports
from parsing_trs import TRSParser
import utils_trsproc

console = Console()

dicoPhases = {
	'-cne':("Effacement de l'annotation en Entités Nommées", "Cleaning NE annotation from TRS in", 'trs', TRSParser.cleanNEfromTRS),
	'-crt':("Correction de TRS selon problèmes rencontrées", "TRS custom correction in", 'trs', utils_trsproc.turnDifferenceTRS),
	'-ne':("Extraction d'Entités Nommées à partir de TRS", "NE extraction from", 'trs', TRSParser.retrieveNEToTsv),
	'-pne':("Pré-anotation de TRS en Entités Nommées", "NE pre-annotation for TRS in", 'trs', utils_trsproc.trsPreannotation),
	##### WORKING IN PROGRESS
	'-rpt':("Rapport de validation sur Section cible", "Creating validation report for target Section", 'trs', utils_trsproc.soge6ptsReport),
	'-rs':("Echantillonage aléatoire de segments", "Extracting random segments from", 'trs', utils_trsproc.randomSampling),
	'-rsne':("Echantillonage aléatoire d'entité nommées", "Extracting random NE from", 'trs', utils_trsproc.randomSamplingNE),
	'-tg':("Conversion de TRS à TextGrid", "Converting to TextGrid in", 'trs', TRSParser.trsToTextGrid),
	'-tgrs':("Conversion de TextGrid à TRS", "Converting TextGrid to TRS in", 'TextGrid', TRSParser.textGridToTRS),
	'-tmp':("Création TRS temporaire", "Writing temporary TRS in", 'trs', TRSParser.trsTMP),
	'-trs':("Réecriture TRS", "Re-writing TRS in", 'txt', TRSParser.txtToTrs),
	'-tsv':("Conversion de TRS à tsv", "Writing tsv from TRS in", 'trs', TRSParser.trsToTsv),
	'-txt':("Création de txt et TRS-placeholder pour réecriture", "Extracting txt and TRS-placeholder in", 'trs', TRSParser.trsToTxt),
	'-vad':("Conversion de TextGrid VAD à TRS", "Converting TextGrid in", 'TextGrid', TRSParser.vadToTRS),
	'-vsi':("Création tableau d'information sur les TRS pour validation", "Extracting TRS statistics in", 'trs', TRSParser.validateTRS)
}

#----------
def main():
	start_time = time.time()

	try:
		p = sys.argv[1]
		if len(sys.argv) == 3:
			docPath = sys.argv[2]
		else:
			docPath = os.getcwd()

		procParam = dicoPhases[p]
		docus = sorted(glob.glob(os.path.join(docPath, f'*.{procParam[2]}')))
		docus = list(set(docus))
		fun = procParam[-1]
		if p in ["-rs", "-rsne"]:
			fun(docus, docPath)
		else:
			with console.status(f"{procParam[1]} {docPath} with {len(docus)} files", spinner='point') as status:
				for d in docus:
					if procParam[2] == 'trs':
						ff = TRSParser(d)
						#print(ff.speakers)	# DEBUG
						fun(ff)
						#print(ff.filename, ff.contents[0]['totalWords']) # DEBUG
					else:
						fun(d)
			console.print(status)
	except (IndexError, KeyError):
		utils_trsproc.warningArgs(dicoPhases)

	print("--- %s sec taken ---" % round((time.time() - start_time), 2))

if __name__ == '__main__':
	main()	