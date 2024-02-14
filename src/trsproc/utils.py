#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
##
### complementary functions for TRS processing
#### trsproc direct dependency
#####

#Global imports
import random
random.seed(42)

import os, re
import json
import parselmouth

# Custom imports
from .parser import TRSParser

script_dir = os.path.dirname(__file__)

#----------
def importJson(json_input):
    """
    >_ json file
    >>> python dict
    """
    with open(json_input, 'r', encoding='utf-8') as f:

        return json.load(f)


def tmpReport(trs_input, section_type="report"):
    """
    >_ TRS file for statistical validation only in the specified section
    >>> Section validation report, table with segments < 10s and pauses > 0.5s
    """
    trs_tmp = TRSParser.trsTMP(trs_input, section_type)
    folder_out = trs_input.corpus
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
            with open(tab_out, 'w', encoding='utf-8') as f:
                f.write("file_name\tdur_tot\tdur_section\tseg_type\tseg_dur\tseg_start\tseg_end\tnb_token\tcontent")
        with open(tab_out, 'a', encoding='utf-8') as f_tsv:
            print(f"Pauses longer than 0.5 s -> ", nb_silence_no)
            for x in silence_no:
                f_tsv.write(f"\n{t.filename}\t{trs_input.fileduration}\t{t.sectionduration}\tsilence\t{x['duration']}\t{x['xmin']}\t{x['xmax']}\t{x['tokens']}\t{x['content']}")
            print(f"Segments longer than 10 s -> ", nb_speech_no)
            for y in speech_no:
                f_tsv.write(f"\n{t.filename}\t{trs_input.fileduration}\t{t.sectionduration}\tspeech\t{y['duration']}\t{y['xmin']}\t{y['xmax']}\t{y['tokens']}\t{y['content']}")
    
    return

def sampleFromDict(input_dict, sample):
    keys = random.sample(list(input_dict.keys()), sample)
    values = [input_dict[k] for k in keys]

    return values


def randomSampling(list_trs, save_path):
    """
    >_ TRS list from which to extract random segments
    >>> minimum sample size based on population input, table with random sampled segments from population, audio segment files
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
                population[(trs.filename, s, trs.audiofile)] = (trs.filename, str(trs.contents[s]['xmin']), trs.contents[s]['content'], trs.contents[s]['content'], str(trs.contents[s]['xmax']), str(trs.contents[s]['duration']), str(s), str(trs.contents[s]['tokens']), spk_name, spk_sex, str(trs.contents[s]['SNR']))
    sample_use = input(f"Use {minimum_sample} as sample size? (y/n)\t")
    if re.search("y", sample_use.lower()):
        population_sample = sampleFromDict(population, minimum_sample)
        tabSample = os.path.join(save_path, f"sample_segments_{minimum_sample}.tsv")
    else:
        sample_size = int(input("Provide new sample size\t"))
        population_sample = sampleFromDict(population, sample_size)
        tabSample = os.path.join(save_path, f"sample_segments_{sample_size}.tsv")
    with open(tabSample, 'w', encoding='utf-8') as f:
        f.write("file_name\tsegment_start\ttranscription\tcorrection\tsegment_end\tsegment_duration\tsegment_id\tnb_tokens\tspeaker_name\tspeaker_sex\tSNR")
        for o in population_sample:
            f.write("\n{}".format("\t".join(o)))
            try:
                sample_audio = parselmouth.Sound(o[2])
                sample_audio = sample_audio.extract_part(population_sample[o][1], population_sample[o][4])
                sample_out = os.path.join(save_path, f"{population_sample[o][0]}_{o[1]}.wav")
                sample_audio.save(sample_out, "WAV")
            except(FileNotFoundError, parselmouth.PraatError, ValueError):
                pass
    print(f"\N{BOOKMARK} Samples saved in {tabSample}")

    return


def randomSamplingNE(list_trs, save_path):
    """
    >_ TRS list from which extracting random named entities
    >>> minimum sample size based on population input, table with random sampled named entities from population, 
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
    with open(tabSample, 'w', encoding='utf-8') as f:
        f.write("file_name\tNE_start\tNE_class\ttranscription\tNE_class_correction\tcorrection\tNE_id\tspeaker_name\tspeaker_sex")
        for o in population_sample:
            f.write("\n{}".format("\t".join(o)))
            try:
                sample_audio = parselmouth.Sound(o[2])
                sample_audio = sample_audio.extract_part(population_sample[o][1], population_sample[o][4])
                sample_out = os.path.join(save_path, f"{population_sample[o][0]}_NE-{o[1]}.wav")
                sample_audio.save(sample_out, "WAV")
            except(FileNotFoundError, parselmouth.PraatError, ValueError):
                pass
    print(f"\N{BOOKMARK} NE Samples saved in {tabSample}")
    
    return


def createUpdateDictNE(table_info, ne_dict, ne_origin):
    """
    >_ table with extracted NE from TRS
    >>> update or creation of NE-dict for pre-annotation
    """
    try:
        neSet = importJson(ne_dict)
        neDict = neSet[1]
        neSources = neSet[0]
        if ne_origin not in neSources:
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
            print(f'\N{WARNING SIGN} found new class "{ne_content}" : {neDict[ne_content]} vs. {ne_type}\n{i}')
        else:
            neDict[ne_content] = ne_type
    neSet = [neSources, neDict]
    with open(ne_dict, 'w', encoding='utf-8') as f:
        f.write(json.dumps(neSet))

    return neDict


def trsPreannotation(input_trs: TRSParser):
    """
    >_ TRS file
    >>> TRS pre-annotated using the specified NE-dict
    """
    dictNE = os.path.join(input_trs.filepath, f'{input_trs.corpus}_NE-reference.json')
    tableInfo = os.path.join(input_trs.filepath, f'{input_trs.corpus}_NE-extraction.tsv')
    if os.path.isfile(tableInfo):
        dictNE = createUpdateDictNE(tableInfo, dictNE, os.path.basename(input_trs.filepath))
    else:
        dictNE = importJson(dictNE)
    #print(dictNE) #DEBUG
    #cpt = 0 #DEBUG
    list_ne_len1_plus = []
    for k in dictNE[1].keys():
        if len(k.split()) > 1:
            #cpt += 1 #DEBUG
            #print(cpt, k) #DEBUG
            list_ne_len1_plus.append(k)
    new_d = preAnnotateNElen1(input_trs, dictNE[1])
    preAnnotateNElenPlus(new_d, list_ne_len1_plus, dictNE[1])

    return


def preAnnotateNElen1(input_trs: TRSParser, dict_ne):
    """
    >_ TRS for NE pre-annotation
    >>> TRS pre-annotated with NE of length 1
    """
    trs_preannotated = ""
    trs_output = os.path.join(input_trs.filepath, "preannotated", f'{input_trs.filename}.trs')
    os.makedirs(os.path.join(input_trs.filepath, "preannotated"), exist_ok=True)
    print(f'\N{CARD FILE BOX} Preannotating simple NE in {input_trs.filename}...')
    trs_input = open(input_trs.inputTRS, 'r', encoding='utf-8').read()
    trs_list = trs_input.split("\n")
    for l in trs_list:
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
        f_trs.write(trs_preannotated)

    return trs_output


def preAnnotateNElenPlus(input_file, list_ne, dict_ne):
    """
    >_ TRE for pre-annotation of NE of length 2+
    >>> TRS pre-annotated with NE of length 2+
    """
    trs_preannotated = ""
    print(f'\N{CARD FILE BOX} Preannotating complex NE...')
    trs_input = open(input_file, 'r', encoding='utf-8').read()
    trs_list = trs_input.split("\n")
    for l in trs_list:
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
        f_trs.write(trs_preannotated)

    return


## Ad hoc correction functions ---------------
def turnDifferenceTRS(input_trs: TRSParser):
    """
    >_ TRS for which differences in segments might be identified with its twin
    >>> Differences list
    """
    twin_trs_path = os.path.join(input_trs.filepath, "twins", f"{input_trs.filename}.trs")
    twin_trs = TRSParser(twin_trs_path)
    print(f"\N{ABACUS} Searching for segmentation differences between {input_trs.filename} and {twin_trs.filename}")
    for s in input_trs.contents:
        if s in [0, 'NE']:
            pass
        else:
            input_s = input_trs.contents[s]
            twin_s = twin_trs.contents[s]
            if input_s['xmin'] != twin_s['xmin']:
                print(f"Difference found in starting of segment {s} -> {input_s['xmin']} vs. {twin_s['xmin']}")
            if input_s['xmax'] != twin_s['xmax']:
                print(f"Difference found in ending of segment {s} -> {input_s['xmax']} vs. {twin_s['xmax']}")

    return


def trsEmptySpaceBeforeNE(input_trs: TRSParser):
    """
    >_ TRS file in which to add an empty space before each NE
    >>> corrected TRS
    """
    output_trs = ""
    trs = open(input_trs.inputTRS, 'r', encoding='utf-8').read()
    trs_list = trs.split("\n")
    print(f"\N{LINKED PAPERCLIPS} Correcting {input_trs.filename}")
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
        line = line.replace("  ", " ")
        output_trs += f"{line}\n"
    path_correction = os.path.join(input_trs.filepath, "correction", "NE")
    os.makedirs(path_correction, exist_ok=True)
    file_output = os.path.join(path_correction, f"{input_trs.filename}.trs")
    with open(file_output, 'w', encoding='utf-8') as f_txt:
        f_txt.write("".join(output_trs))
    
    return


def correctionLà(input_trs: TRSParser):
    """
    >_ TRS file for correction of sentences ending with là
    >>> corrected txt from the origin TRS
    """
    txt_dump, nb_la = "", 0
    txt_folder = os.path.join(input_trs.filepath, "txt")
    txt_input = os.path.join(txt_folder, f"{input_trs.filename}.txt")
    target_path = os.path.join(input_trs.filepath, "corrections", "la")
    os.makedirs(target_path, exist_ok=True)
    txt_output = os.path.join(target_path, f"{input_trs.filename}.txt")
    txt_input = open(txt_input, 'r', encoding='utf-8').read()
    txt_input = txt_input.split("\n")
    for l in txt_input:
        l_splitted = l.split(" ")
        if re.search("là", l_splitted[-1].lower()):
            nb_la +=1
            l_splitted[-1] = "la"
            l = " ".join(l_splitted)
        txt_dump += f"{l}\n"
    with open(txt_output, 'w', encoding='utf-8') as f_txt:
            f_txt.write(txt_dump)
    print(f'\N{CHECK MARK} Corrected {nb_la} misplaced "là" in {input_trs.filename}')

    return


def correctionMaj(input_trs: TRSParser):
    """
    >_ TRS file for correction of misplaced capiral letters
    >>> corrected TRS
    """
    txt_dump, nb_maj = "", 0
    target_path = os.path.join(input_trs.filepath, "corrections", "maj")
    os.makedirs(target_path, exist_ok=True)
    trs_output = os.path.join(target_path, f"{input_trs.filename}.trs")
    txt_input = open(input_trs.inputTRS, 'r', encoding='utf-8').read()
    txt_input = txt_input.split("\n")
    nb_l = len(txt_input)
    for l in range(nb_l):
        line = txt_input[l]
        if re.search("<.*>", line):
            pass
        else:
            is_entity = re.search('extent="begin" type="entities"', txt_input[l-1])
            if is_entity:
                try:
                    line = line[0].upper() + line[1:]
                    nb_maj += 1
                except IndexError:
                    pass
            elif  re.search("nontrans", line):
                pass
            else:
                try:
                    line = line[0].lower() + line[1:]
                    nb_maj += 1
                except IndexError:
                    pass
        txt_dump += f"{line}\n"
    with open(trs_output, 'w', encoding='utf-8') as f_out:
            f_out.write(txt_dump)
    print(f'\N{CHECK MARK} Corrected {nb_maj} misplaced CAPITAL in {input_trs.filename}')

    return
