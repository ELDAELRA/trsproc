#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Fonction complémentaires pour le traitement de fichiers TRS
## trsproc.py dependency
### 17/08-22/12/2023
#### Gabriele CHIGNOLI
#####
#
# module à importer
#

#Global imports
import random
random.seed(42)

import os, re
from xml.etree import cElementTree as ElementTree
import json
import parselmouth

# Custom imports
from parsing_trs import TRSParser

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

#----------
def warningArgs(args_dict):
	print(f"Invalid arguments. Please choose from the list of flags below and call the program again:")
	for p in args_dict:
		print(f"{p} -> {args_dict[p][0]}")

	return


def importJson(json_input):
	"""
	>_ json contenant un dict
	>>> dictionnaire
	"""
	with open(json_input, 'r', encoding='utf-8') as f:

		return json.load(f)


def praatSNRforSegment(audio, seg_start, seg_end):
	"""
	>_audio file, timestaps for start and end of segment
	>>> segment SNR
	"""
	sound = parselmouth.Sound(audio)
	sound_part = sound.extract_part(seg_start, seg_end)
	# parole superposée 20 < SNR > 45
	hnr = sound_part.to_harmonicity()
	mean_snr = parselmouth.praat.call(hnr, "Get mean", 0, 0)

	return round(mean_snr, 2)


def soge6ptsReport(trs_input, section_type="report"):
	"""
	>_ Fichier TRS à valider selon les 6 points du projet SoGe (ELDA-0774)
	- create TMP folder with copy of original TRS retaining only the report part ?
	>>> Rapport de validation
	"""
	trs_tmp = TRSParser.trsTMP(trs_input, section_type)
	folder_out = os.path.basename(trs_input.filepath)
	tab_out = os.path.join(trs_input.filepath, "tmp", f'summary_report-{folder_out}.tsv')
	for t in trs_tmp:
		t = TRSParser(t, lang=trs_input.lang)
		TRSParser.validateTRS(t)
		seg_tot = t.contents[0]['totalSegments']
		nb_silence_ok, nb_silence_no, nb_speech_ok, nb_speech_no = 0, 0, 0, 0
		silence_ok, silence_no, speech_ok, speech_no = [], [], [], []
		for s in range(1, seg_tot+1):
			seg_test = t.contents[s]
			if seg_test['content'] == '[nontrans]':
				if seg_test['duration'] >= 0.6:
					nb_silence_no += 1
					silence_no.append(seg_test)
				else:
					nb_silence_ok += 1
					silence_ok.append(seg_test)
			else:
				if seg_test['duration'] < 11:
					nb_speech_ok += 1
					speech_ok.append(seg_test)
				else:
					nb_speech_no += 1
					speech_no.append(seg_test)
		try:
			open(tab_out).close()
		except FileNotFoundError:
		 ## Teste si un tableau existe déjà sinon en crée un avec en-tête
			with open(tab_out, 'w', encoding='utf-8') as f:
				f.write("file_name\tdur_tot\tdur_section\tseg_type\tseg_dur\tseg_start\tseg_end\tnb_token\tcontent")
			 ## Ajout des infos dans le tableau de récap
		with open(tab_out, 'a', encoding='utf-8') as f_tsv:
			print(f"Nombre de pauses supérieures à 0.5 s -> ", nb_silence_no)
			for x in silence_no:
				f_tsv.write(f"\n{t.filename}\t{trs_input.fileduration}\t{t.sectionduration}\tsilence\t{x['duration']}\t{x['xmin']}\t{x['xmax']}\t{x['tokens']}\t{x['content']}")
			print(f"Nombre de segments supérieures à 10 s -> ", nb_speech_no)
			for y in speech_no:
				f_tsv.write(f"\n{t.filename}\t{trs_input.fileduration}\t{t.sectionduration}\tspeech\t{y['duration']}\t{y['xmin']}\t{y['xmax']}\t{y['tokens']}\t{y['content']}")
	
#TODO
	# frontière ok ? audio = texte
	# mots coupés ?
	# bon locuteur
#Si balise Who est detectee et que le segment n'est pas vide <- signaler dans tableau segments problematiques

	return


def turnDifferenceTRS(trs_t, folder_q, tag=["Turn"]):
	"""
	>_ Nom d'un TRS pour lequel identifier une différence de Turn ou Sync avec son jumeau
	>>> Liste des différences
	"""
	path_trs_t, trs_name = os.path.split(trs_t)
	folder_trs_t = os.path.basename(path_trs_t)
	path_trs_q = path_trs_t.rstrip(folder_trs_t)
	trs_q = os.path.join(path_trs_q, folder_q, f"{trs_name[:-4]}_*.trs")
#	print(trs_t, trs_q)
	trs_q_name = os.path.split(trs_q)[1]
	for t in tag:
		print(f"\N{ABACUS} Searching differences in {t} between {trs_name} and {trs_q_name}")
		if t == "Turn":
		 ## Retrieve tag information for reference TRS
			tag_list_t, tag_list_q = [], []
			tree_t = ElementTree.parse(trs_t)
			root_t = tree_t.getroot()
			for tags_t in root_t.iter(t):
				tag_t_start, tag_t_end = tags_t.attrib['startTime'], tags_t.attrib['endTime']
				tag_list_t.append((tag_t_start, tag_t_end))
		 ## Retrieve tag information for test TRS
			tree_q = ElementTree.parse(trs_q)
			root_q = tree_q.getroot()
			for tags_q in root_q.iter(t):
				tag_q_start, tag_q_end = tags_q.attrib['startTime'], tags_q.attrib['endTime']
				tag_list_q.append((tag_q_start, tag_q_end))
		print(f"Ref {tag_list_t} vs Test {len(tag_list_q)}")

	return


def trsFinalCorrection(input_trs):
	"""
	>_ fichier trs sur lequel appliquer une correction
	>>> fichier trs corrigé
	"""
	output_trs = ""
	trs_folder, trs_name = os.path.split(input_trs)
	trs_name = input_trs[:-4]
	trs = open(input_trs, 'r', encoding='utf-8').read()
	trs_list = trs.split("\n")
	print(f"\N{LINKED PAPERCLIPS} Correcting {trs_name}")
	 ### Boucle sur les lignes du TRS
	for l in range(len(trs_list)):
		line = trs_list[l]
		if len(line) == 0 or re.search("<.*>", line):
			pass
		else:
			line_succ = trs_list[l+1]
			line_prec = trs_list[l-1]
			if re.search("<Event.*entities.*", line_succ) and re.search('extent="begin"', line_succ):
				line = line + " "
			if re.search("<Event.*entities.*", line_prec) and re.search('extent="end"', line_prec) and line[0] not in [",", "."]:
				line = " " + line
				### Correction majuscules dans date et amount
				#if re.search('desc="time.*', line_prec) or re.search('desc="amount.*', line_prec):
				#	line = line.lower()
		line = line.replace("  ", " ")
		output_trs += f"{line}\n"

	path_correction = os.path.join(trs_folder, "correction")
	os.makedirs(path_correction, exist_ok=True)
	file_output = os.path.join(path_correction, f"{trs_name}.trs")
	with open(file_output, 'w', encoding='utf-8') as f_txt:
		f_txt.write("".join(output_trs))
	
	return


def sampleFromDict(input_dict, sample):
	keys = random.sample(list(input_dict.keys()), sample)
	values = [input_dict[k] for k in keys]

	return values


def randomSampling(list_trs, save_path):
	"""
	>_ TRS list from which extracting random segments
	>>> minimum sample size based on population input, table with random sampled segments from population
	"""
	population_size = int(input("Enter population size\t"))
	minimum_sample = round((((3.84*(0.5*(1-0.5)))/(0.05*0.05))/(1+(3.84*(0.5*(1-0.5)))/((0.05*0.05)*population_size))))
	print(f"\N{NERD FACE} Based on population size {population_size} minimum sample is: {minimum_sample}")
	population = {}
	for t in list_trs:
		trs = TRSParser(t)
		for s in trs.contents:
			if s not in ['NE', 0] and trs.contents[s]['content'] != "[nontrans]":
				spk_name = trs.speakers[trs.contents[s]['speaker']][0]
				spk_sex = trs.speakers[trs.contents[s]['speaker']][1]
				population[(trs.filename, s)] = (trs.filename, str(trs.contents[s]['xmin']), trs.contents[s]['content'], trs.contents[s]['content'], str(trs.contents[s]['xmax']), str(trs.contents[s]['duration']), str(s), str(trs.contents[s]['tokens']), spk_name, spk_sex)
	sample_use = input(f"Use {minimum_sample} as sample size? (y/n)\t")
	if re.search("y", sample_use.lower()):
		population_sample = sampleFromDict(population, minimum_sample)
		tabSample = os.path.join(save_path, f"sample_segments_{minimum_sample}.tsv")
	else:
		sample_size = int(input("Provide new sample size\t"))
		population_sample = sampleFromDict(population, sample_size)
		tabSample = os.path.join(save_path, f"sample_segments_{sample_size}.tsv")
	#random_files = random.sample(docus, 3)
	with open(tabSample, 'w', encoding='utf-8') as f:
		f.write("file_name\tsegment_start\ttranscription\tcorrection\tsegment_end\tsegment_duration\tsegment_id\tnb_tokens\tspeaker_name\tspeaker_sex")
		for o in population_sample:
			f.write("\n{}".format("\t".join(o)))
	
	return print(f"\N{BOOKMARK} Samples saved in {tabSample}")


def randomSamplingNE(list_trs, save_path):
	"""
	>_ TRS list from which extracting random named entities
	>>> minimum sample size based on population input, table with random sampled named entities from population
	"""
	population_size = int(input("Enter population size\t"))
	minimum_sample = round((((3.84*(0.5*(1-0.5)))/(0.05*0.05))/(1+(3.84*(0.5*(1-0.5)))/((0.05*0.05)*population_size))))
	print(f"\N{NERD FACE} Based on population size {population_size} minimum sample is: {minimum_sample}")
	population = {}
	for t in list_trs:
		trs = TRSParser(t)
		for ne in trs.contents['NE']:
			s = trs.contents['NE'][ne]['segmentID']
			spk_name = trs.speakers[trs.contents[s]['speaker']][0]
			spk_sex = trs.speakers[trs.contents[s]['speaker']][1]
			population[(trs.filename, ne)] = (trs.filename, str(trs.contents['NE'][ne]['xmin']), trs.contents['NE'][ne]['class'], trs.contents['NE'][ne]['content'], trs.contents['NE'][ne]['class'], trs.contents['NE'][ne]['content'], str(ne), spk_name, spk_sex)
		f.write("file_name\tNE_start\tNE_class\ttranscription\tNE_class_correction\tcorrection\tNE_id\tspeaker_name\tspeaker_sex")
	sample_use = input(f"Use {minimum_sample} as sample size? (y/n)\t")
	if re.search("y", sample_use.lower()):
		population_sample = sampleFromDict(population, minimum_sample)
		tabSample = os.path.join(save_path, f"sample_ne_{minimum_sample}.tsv")
	else:
		sample_size = int(input("Provide new sample size\t"))
		population_sample = sampleFromDict(population, sample_size)
		tabSample = os.path.join(save_path, f"sample_ne_{sample_size}.tsv")
	#random_files = random.sample(docus, 3)
	with open(tabSample, 'w', encoding='utf-8') as f:
		f.write("file_name\tNE_start\tNE_class\ttranscription\tNE_class_correction\tcorrection\tNE_id\tspeaker_name\tspeaker_sex")
		for o in population_sample:
			f.write("\n{}".format("\t".join(o)))
	
	return print(f"\N{BOOKMARK} NE Samples saved in {tabSample}")


def createUpdateDictNE(table_info, ne_dict, ne_origin):
	"""
	>_ table avec les NE extraites de trs
	>>> dictionnaire de NE pour pre-annotation et sauvegarde de celui-ci
	"""
	try:
		neSet = importJson(ne_dict)
		neDict = neSet[1]
		neSources = neSet[0]
		neSources.append(ne_origin)
		print(f'\N{CARD FILE BOX} Updating existing NE dict {ne_dict}...')
	except FileNotFoundError:
		neSources, neDict = [ne_origin], {}
		print(f'\N{CARD FILE BOX} Creating NE dict {ne_dict}...')
	#print(neDict) #DEBUG
	tsv_input = open(table_info, 'r', encoding='utf-8').read()
	tsv_list = tsv_input.split("\n")
	for i in tsv_list[1:-2]:
		#file_name timecode NE_rank NE_type NE_content
		ne_type, ne_content = i.split("\t")[3], i.split("\t")[4]
		if ne_content in neDict.keys() and ne_type != neDict[ne_content]:
			print(f'\N{WARNING SIGN} nouvelle classe trouvée pour "{ne_content}" : {neDict[ne_content]} vs. {ne_type}\n{i}')
		else:
			neDict[ne_content] = ne_type
	neSet = [neSources, neDict]
	## Ajout des infos dans le tableau de recap
	with open(ne_dict, 'w', encoding='utf-8') as f:
		f.write(json.dumps(neSet))

	return neDict


def trsPreannotation(input_trs: TRSParser):
	"""
	>_ fichier trs
	>>> trs preannoté en NE suivant le tableau fourni
	"""
	dictNE = os.path.join(script_dir, "langrsrc", f'{os.path.basename(input_trs.filepath)}_NE_reference.json')
	tableInfo = os.path.join(input_trs.filepath, f'{os.path.basename(input_trs.filepath)}_NE_extraction.tsv')
	if os.path.isfile(tableInfo):
		dictNE = createUpdateDictNE(tableInfo, dictNE, os.path.basename(input_trs.filepath))
	else:
		dictNE = importJson(dictNE)
	#print(dictNE) #DEBUG
	#cpt = 0
	list_ne_len1_plus = []
	for k in dictNE[1].keys():
		if len(k.split()) > 1:
			#cpt += 1
			#print(cpt, k)
			list_ne_len1_plus.append(k)
	new_d = preAnnotateNElen1(input_trs, dictNE[1])
	preAnnotateNElenPlus(new_d, list_ne_len1_plus, dictNE[1])

	return


def preAnnotateNElen1(input_trs: TRSParser, dict_ne):
	"""
	>_ trs pour l'extraction d'entités nommées
	>>> trs preannoté avec entités de longeur 1
	"""
	trs_preannotated = ""
	trs_output = os.path.join(input_trs.filepath, "preannotated", f'{input_trs.filename}.trs')
	os.makedirs(os.path.join(input_trs.filepath, "preannotated"), exist_ok=True)
	print(f'\N{CARD FILE BOX} Preannotating simple NE in {input_trs.filename}...')
	trs_input = open(input_trs.inputTRS, 'r', encoding='utf-8').read()
	trs_list = trs_input.split("\n")
	for l in trs_list:
	 ## Boucle sur le TRS et extraction des infos
		if re.search("<.*>", l) or l == "":
			trs_preannotated += f'{l}\n'
		else:
			l_cleaned = l.replace("'", "' ")
			l_splitted = l_cleaned.split(" ")
			new_l = []
			#print("old line", l) #DEBUG
			for i in range(len(l_splitted)):
				m = l_splitted[i]
				if m in dict_ne.keys():
					#print(f'FOUND {m} IN {l}') #DEBUG
					ne_type = dict_ne[m]
					new_m = f'\n<Event desc="{ne_type}" type="entities" extent="begin"/>\n{m}\n<Event desc="{ne_type}" type="entities" extent="end"/>\n'
					new_l.append(new_m)
					#print("new line", new_l) #DEBUG
				else:
					new_l.append(m)
			new_l = " ".join(new_l)
			new_l = new_l.replace("' ", "'")
			trs_preannotated += f'{new_l}\n'
	with open(trs_output, 'w', encoding='utf-8') as f_trs:
	 ## Dump du texte de sortie dans le nouveau TRS
		f_trs.write(trs_preannotated)

	return trs_output


def preAnnotateNElenPlus(input_file, list_ne, dict_ne):
	"""
	>_ trs pour la pre-annotation de NE de longeurs 2+
	>>> trs preannoté avec NE de longueur 2+
	"""
	trs_preannotated = ""
	print(f'\N{CARD FILE BOX} Preannotating complex NE...')
	## Répère les différents noms de fichiers et chemins
	trs_input = open(input_file, 'r', encoding='utf-8').read()
	trs_list = trs_input.split("\n")
	for l in trs_list:
		## Boucle sur le TRS et extraction des infos
		has_ne = False
		if re.search("<.*>", l) or l == "":
			if re.search("nontrans", l):
				trs_preannotated += f'{l}\n\n'
			else:
				trs_preannotated += f'{l}\n'
		else:
			for ne in list_ne:
				if re.search(ne, l):
					has_ne = True
					matched_ne = re.search(ne, l)
					ne_type = dict_ne[ne]
					new_m = f'\n<Event desc="{ne_type}" type="entities" extent="begin"/>\n{ne}\n<Event desc="{ne_type}" type="entities" extent="end"/>\n'
					new_l = l[:matched_ne.start()] + new_m + l[matched_ne.end()+1:]
					#print("NEW LINE", new_l) #DEBUG
			if has_ne == True:
				trs_preannotated += f'{new_l}\n'
			else:
				trs_preannotated += f'{l}\n'
	with open(input_file, 'w', encoding='utf-8') as f_trs:
		## Dump du texte de sortie dans le nouveau TRS
		f_trs.write(trs_preannotated)

	return
