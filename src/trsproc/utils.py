#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
##
### complementary functions for TRS processing
#### trsproc direct dependency
#####

import csv
import json
import os
import random
import re
from collections import defaultdict
from pathlib import Path
from xml.etree import cElementTree as ElementTree

# TODO: Perhaps import large audio libraries only when necessary
import librosa
import parselmouth
import soundfile as sf

from .parser import TRSParser

random.seed(42)
script_dir = os.path.dirname(__file__)


# ----------
def parse_json(json_input):
    """
    >_ json file
    >>> python dict
    """
    with open(json_input, "r", encoding="utf-8") as f:
        return json.load(f)


def tmp_report(trs_input, section_type="report"):
    """
    >_ TRS file for statistical validation only in the specified section
    >>> Section validation report, table with segments < 10s and pauses > 0.5s
    """
    trs_tmp = TRSParser.trs_tmp(trs_input, section_type)
    folder_out = trs_input.corpus
    tab_out = os.path.join(
        trs_input.filepath, "tmp", f"summary_report-{folder_out}.tsv"
    )
    for t in trs_tmp:
        t = TRSParser(t, lang=trs_input.lang)
        TRSParser.validate_trs(t)
        seg_tot = t.contents[0]["totalSegments"]
        nb_silence_ok, nb_silence_no, nb_speech_ok, nb_speech_no = 0, 0, 0, 0
        silence_ok, silence_no, speech_ok, speech_no = [], [], [], []
        for seg_id in range(1, seg_tot + 1):
            seg_test = t.contents[seg_id]
            if seg_test["content"] == "[nontrans]":
                if seg_test["duration"] >= 0.6:
                    nb_silence_no += 1
                    silence_no.append(seg_test)
                else:
                    nb_silence_ok += 1
                    silence_ok.append(seg_test)
            else:
                if seg_test["duration"] < 11:
                    nb_speech_ok += 1
                    speech_ok.append(seg_test)
                else:
                    nb_speech_no += 1
                    speech_no.append(seg_test)
        try:
            open(tab_out).close()
        except FileNotFoundError:
            with open(tab_out, "w", encoding="utf-8") as f:
                f.write(
                    "file_name\tdur_tot\tdur_section\tseg_type\tseg_dur\tseg_start\tseg_end\tnb_token\tcontent"
                )
        with open(tab_out, "a", encoding="utf-8") as f_tsv:
            print(f"Pauses longer than 0.5 s -> {nb_silence_no}")
            for x in silence_no:
                f_tsv.write(
                    f"\n{t.filename}\t{trs_input.file_duration}\t{t.section_duration}\tsilence\t{x['duration']}\t{x['xmin']}\t{x['xmax']}\t{x['tokens']}\t{x['content']}"
                )
            print(f"Segments longer than 10 s -> {nb_speech_no}")
            for y in speech_no:
                f_tsv.write(
                    f"\n{t.filename}\t{trs_input.file_duration}\t{t.section_duration}\tspeech\t{y['duration']}\t{y['xmin']}\t{y['xmax']}\t{y['tokens']}\t{y['content']}"
                )

    return


def sample_from_dict(input_dict, sample):
    keys = random.sample(list(input_dict.keys()), sample)
    values = [input_dict[k] for k in keys]

    return values


def random_sampling(list_trs, save_path):
    """
    >_ TRS list from which to extract random segments
    >>> minimum sample size based on population input, table with random sampled segments from population, audio segment files
    """
    valid_population = False
    while not valid_population:
        try:
            population_size = int(input("Enter population size\t"))
            if population_size <= 0:
                raise ValueError
            valid_population = True
        except ValueError:
            print("\N{WARNING SIGN} Invalid input. Please enter a positive integer.")

    minimum_sample = round(
        (
            ((3.84 * (0.5 * (1 - 0.5))) / (0.05 * 0.05))
            / (1 + (3.84 * (0.5 * (1 - 0.5))) / ((0.05 * 0.05) * population_size))
        )
    )
    print(
        f"\N{NERD FACE} Based on population size {population_size} minimum sample is: {minimum_sample}"
    )
    population = {}
    for t in list_trs:
        trs = TRSParser(t)
        for s in trs.contents:
            if s not in ["NE", 0] and trs.contents[s]["content"] != "[nontrans]":
                speaker_field = trs.contents[s].get("speaker", "NA")

                # Skip segments that involve multiple speakers (e.g., "sp1 sp3")
                if isinstance(speaker_field, str) and len(speaker_field.split()) > 1:
                    continue

                spk_name = (
                    trs.speakers[trs.contents[s]["speaker"]][0]
                    if trs.contents[s].get("speaker") != "NA"
                    else "NA"
                )
                spk_sex = (
                    trs.speakers[trs.contents[s]["speaker"]][1]
                    if trs.contents[s].get("speaker") != "NA"
                    else "NA"
                )
                population[(trs.filename, s, trs.audio_file)] = (
                    trs.filename,
                    str(trs.contents[s]["xmin"]),
                    trs.contents[s]["content"],
                    str(trs.contents[s]["xmax"]),
                    str(trs.contents[s]["duration"]),
                    str(s),
                    str(trs.contents[s]["tokens"]),
                    spk_name,
                    spk_sex,
                    str(trs.contents[s]["SNR"]),
                )

    if len(population.keys()) < population_size:
        population_size = len(population.keys())
        minimum_sample = round(
            (
                ((3.84 * (0.5 * (1 - 0.5))) / (0.05 * 0.05))
                / (1 + (3.84 * (0.5 * (1 - 0.5))) / ((0.05 * 0.05) * population_size))
            )
        )
        print(
            f"Adjusted population size to {population_size}, new minimum sample: {minimum_sample}"
        )

    sample_use = input(f"Use {minimum_sample} as sample size? (y/n)\t")

    if len(population.keys()) == 0:
        # Generate a warning if no segments found in the provided TRS files
        print("\N{WARNING SIGN} No segments found in the provided TRS files")
        return
    if minimum_sample > len(population.keys()):
        print(
            "\N{WARNING SIGN} Sample size is larger than population size, please provide a new sample size"
        )
        return

    if re.search("y", sample_use.lower()):
        population_sample = sample_from_dict(population, minimum_sample)
        tab_sample = os.path.join(save_path, f"sample_segments_{minimum_sample}.tsv")
    else:
        sample_size = int(input("Provide new sample size\t"))
        population_sample = sample_from_dict(population, sample_size)
        tab_sample = os.path.join(save_path, f"sample_segments_{sample_size}.tsv")
    with open(tab_sample, "w", encoding="utf-8") as f:
        f.write(
            "file_name\tsegment_start\ttranscription\tsegment_end\tsegment_duration\tsegment_id\tnb_tokens\tspeaker_name\tspeaker_sex\tSNR"
        )
        for o in population_sample:
            f.write("\n{}".format("\t".join(o)))
            try:
                sample_audio = parselmouth.Sound(o[0] + ".wav")
                sample_audio = sample_audio.extract_part(
                    float(population_sample[o][1]), float(population_sample[o][3])
                )
                sample_out = os.path.join(
                    save_path, f"{population_sample[o][0]}_{o[1]}.wav"
                )
                sample_audio.save(sample_out, "WAV")
            except (FileNotFoundError, parselmouth.PraatError, ValueError):
                pass
    print(f"\N{BOOKMARK} Samples saved in {tab_sample}")

    return tab_sample


def random_sampling_ne(list_trs: list[Path], save_path: Path) -> None:
    """
    >_ TRS list from which extracting random named entities
    >>> minimum sample size based on population input, table with random sampled named entities from population,
    """

    valid_population = False
    while not valid_population:
        try:
            population_size = int(input("Enter population size\t"))
            if population_size <= 0:
                raise ValueError
            valid_population = True
        except ValueError:
            print("\N{WARNING SIGN} Invalid input. Please enter a positive integer.")

    minimum_sample = round(
        (
            ((3.84 * (0.5 * (1 - 0.5))) / (0.05 * 0.05))
            / (1 + (3.84 * (0.5 * (1 - 0.5))) / ((0.05 * 0.05) * population_size))
        )
    )
    print(
        "\N{NERD FACE} Based on population size {population_size} minimum sample is: {minimum_sample}"
    )
    population = {}
    for t in list_trs:
        trs = TRSParser(t)
        for ne in trs.contents["NE"]:
            s = trs.contents["NE"][ne]["segmentID"]
            spk_name = (
                trs.speakers[trs.contents[s]["speaker"]][0]
                if trs.contents[s].get("speaker") != "NA"
                else "NA"
            )
            spk_sex = (
                trs.speakers[trs.contents[s]["speaker"]][1]
                if trs.contents[s].get("speaker") != "NA"
                else "NA"
            )
            nb_ne = len(
                [
                    ne
                    for ne in trs.contents["NE"]
                    if trs.contents["NE"][ne]["segmentID"] == s
                ]
            )
            if (trs.filename, s) not in population:
                population[(trs.filename, s)] = []
            population[(trs.filename, s)].append(
                (
                    trs.filename,
                    str(trs.contents[s]["xmin"]),
                    trs.contents["NE"][ne]["class"],
                    trs.contents["NE"][ne]["content"],
                    trs.contents[s]["content"],
                    str(trs.contents[s]["xmax"]),
                    str(trs.contents[s]["duration"]),
                    str(s),
                    str(ne),
                    str(trs.contents[s]["tokens"]),
                    str(nb_ne),
                    spk_name,
                    spk_sex,
                )
            )

    sample_use = input(f"Use {minimum_sample} as sample size? (y/n)\t")

    if len(population.keys()) == 0:
        # Generate a warning if no NE found in the provided TRS files
        print("\N{WARNING SIGN} No NE found in the provided TRS files")
        return
    if minimum_sample > len(population.keys()):
        print(
            "\N{WARNING SIGN} Sample size is larger than population size, please provide a new sample size !"
        )

        return

    if len(population.keys()) == 0:
        # Generate a warning if no NE found in the provided TRS files
        print("\N{WARNING SIGN} No NE found in the provided TRS files")
        return

    if re.search("y", sample_use.lower()):
        population_sample = sample_from_dict(population, minimum_sample)

        tab_sample = os.path.join(save_path, f"sample_ne_{minimum_sample}.tsv")
    else:
        sample_size = int(input("Provide new sample size\t"))
        population_sample = sample_from_dict(population, sample_size)
        tab_sample = os.path.join(save_path, f"sample_ne_{sample_size}.tsv")
    with open(tab_sample, "w", encoding="utf-8") as f:
        f.write(
            "file_name\tsegment_start\tNE_class\tNE_content\ttranscription\tsegment_end\tsegment_duration\tsegment_id\tNE_id\tnb_tokens\tnb_NE\tspeaker_name\tspeaker_sex"
        )
        for o in population_sample:
            for ne in o:
                f.write("\n{}".format("\t".join(ne)))
            try:
                sample_audio = parselmouth.Sound(o[0][0] + ".wav")
                sample_audio = sample_audio.extract_part(
                    float(population_sample[o][0][1]), float(population_sample[o][0][3])
                )
                sample_out = os.path.join(
                    save_path, f"{population_sample[o][0][0]}_NE-{o[0][1]}.wav"
                )
                sample_audio.save(sample_out, "WAV")
            except (FileNotFoundError, parselmouth.PraatError, ValueError):
                pass
    print(f"\N{BOOKMARK} NE Samples saved in {tab_sample}")

    return


def extract_segments(tsv_file: str):
    """
    >_ TSV file with segment information
    >>> WAV segment files extracted to a validation subfolder
    """
    base_dir = os.path.dirname(tsv_file)
    out_dir = os.path.join(base_dir, "validation")
    os.makedirs(out_dir, exist_ok=True)

    segments_by_file = defaultdict(list)

    with open(tsv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            fname = os.path.basename(row["file_name"])
            segments_by_file[fname].append(
                {
                    "seg_id": row["segment_id"],
                    "start": float(row["segment_start"]),
                    "end": float(row["segment_end"]),
                }
            )

    for fname, segments in segments_by_file.items():
        audio_path = os.path.join(base_dir, "..", f"{fname}.wav")

        if not os.path.exists(audio_path):
            print(f"\N{WARNING SIGN} Missing audio: {audio_path}")
            continue

        y, sr = librosa.load(audio_path, sr=None, mono=True)

        for seg in segments:
            seg_id = seg["seg_id"]
            start_sample = round(seg["start"] * sr)
            end_sample = round(seg["end"] * sr)

            start_sample = max(0, min(start_sample, len(y)))
            end_sample = max(0, min(end_sample, len(y)))

            seg_audio = y[start_sample:end_sample]

            if len(seg_audio) == 0:
                print(f"\N{WARNING SIGN} Empty segment (skipped): {fname} / {seg_id}")
                continue

            out_path = os.path.join(out_dir, f"{fname}_{seg_id}.wav")
            sf.write(out_path, seg_audio, sr)
            print(f"\N{BOOKMARK} Saved: {out_path}")

    return


def create_update_dict_ne(table_info, ne_dict, ne_origin):
    """
    >_ table with extracted NE from TRS
    >>> update or creation of NE-dict for pre-annotation
    """
    try:
        neSet = parse_json(ne_dict)
        neDict = neSet[1]
        neSources = neSet[0]
        if ne_origin not in neSources:
            neSources.append(ne_origin)
            print(f"\N{CARD FILE BOX} Updating existing NE dict {ne_dict}...")
    except FileNotFoundError:
        neSources, neDict = [ne_origin], {}
        print(f"\N{CARD FILE BOX} Creating NE dict {ne_dict}...")
    # print(neDict) #DEBUG
    tsv_input = open(table_info, "r", encoding="utf-8").read()
    tsv_list = tsv_input.split("\n")
    for i in tsv_list[1:-2]:
        # file_name timecode NE_rank NE_type NE_content
        ne_type, ne_content = i.split("\t")[3], i.split("\t")[4]
        if ne_content in neDict.keys() and ne_type != neDict[ne_content]:
            print(
                f"\N{WARNING SIGN} found new class '{ne_content}' : {neDict[ne_content]} vs. {ne_type}\n{i}"
            )
        else:
            neDict[ne_content] = ne_type
    neSet = [neSources, neDict]
    with open(ne_dict, "w", encoding="utf-8") as f:
        f.write(json.dumps(neSet))

    return neDict


def trs_preannotation(input_trs: TRSParser):
    """
    >_ TRS file
    >>> TRS pre-annotated using the specified NE-dict
    """
    dictNE = os.path.join(input_trs.filepath, f"{input_trs.corpus}_NE-reference.json")
    tableInfo = os.path.join(
        input_trs.filepath, f"{input_trs.corpus}_NE-extraction.tsv"
    )
    if os.path.isfile(tableInfo):
        dictNE = create_update_dict_ne(
            tableInfo, dictNE, os.path.basename(input_trs.filepath)
        )
    else:
        dictNE = parse_json(dictNE)
    # print(dictNE) #DEBUG
    # cpt = 0 #DEBUG
    list_ne_len1_plus = []
    for k in dictNE[1].keys():
        if len(k.split()) > 1:
            # cpt += 1 #DEBUG
            # print(cpt, k) #DEBUG
            list_ne_len1_plus.append(k)
    new_d = pre_annotate_ne_len1(input_trs, dictNE[1])
    pre_annotate_ne_len_plus(new_d, list_ne_len1_plus, dictNE[1])

    return


def pre_annotate_ne_len1(input_trs: TRSParser, dict_ne):
    """
    >_ TRS for NE pre-annotation
    >>> TRS pre-annotated with NE of length 1
    """
    trs_preannotated = ""
    trs_output = os.path.join(
        input_trs.filepath, "preannotated", f"{input_trs.filename}.trs"
    )
    os.makedirs(os.path.join(input_trs.filepath, "preannotated"), exist_ok=True)
    print(f"\N{CARD FILE BOX} Preannotating simple NE in {input_trs.filename}...")
    trs_input = open(input_trs.input_trs, "r", encoding="utf-8").read()
    trs_list = trs_input.split("\n")
    for line in trs_list:
        if re.search("<.*>", line) or line == "":
            trs_preannotated += f"{line}\n"
        else:
            line_cleaned = line.replace("'", "' ")
            line_splitted = line_cleaned.split(" ")
            new_l = []
            # print("old line", l) #DEBUG
            for token_id in range(len(line_splitted)):
                token = line_splitted[token_id]
                if token in dict_ne.keys():
                    # print(f'FOUND {m} IN {l}') #DEBUG
                    ne_type = dict_ne[token]
                    new_m = f'\n<Event desc="{ne_type}" type="entities" extent="begin"/>\n{token}\n<Event desc="{ne_type}" type="entities" extent="end"/>\n'
                    new_l.append(new_m)
                    # print("new line", new_l) #DEBUG
                else:
                    new_l.append(token)
            new_l = " ".join(new_l)
            new_l = new_l.replace("' ", "'")
            trs_preannotated += f"{new_l}\n"
    with open(trs_output, "w", encoding="utf-8") as f_trs:
        f_trs.write(trs_preannotated)

    return trs_output


def pre_annotate_ne_len_plus(input_file, list_ne, dict_ne):
    """
    >_ TRE for pre-annotation of NE of length 2+
    >>> TRS pre-annotated with NE of length 2+
    """
    trs_preannotated = ""
    print("\N{CARD FILE BOX} Preannotating complex NE...")
    trs_input = open(input_file, "r", encoding="utf-8").read()
    trs_list = trs_input.split("\n")
    for line in trs_list:
        has_ne = False
        if re.search("<.*>", line) or line == "":
            if re.search("nontrans", line):
                trs_preannotated += f"{line}\n\n"
            else:
                trs_preannotated += f"{line}\n"
        else:
            for ne in list_ne:
                if re.search(ne, line):
                    has_ne = True
                    matched_ne = re.search(ne, line)
                    ne_type = dict_ne[ne]
                    new_annotation = f'\n<Event desc="{ne_type}" type="entities" extent="begin"/>\n{ne}\n<Event desc="{ne_type}" type="entities" extent="end"/>\n'
                    new_line = (
                        line[: matched_ne.start()]
                        + new_annotation
                        + line[matched_ne.end() + 1 :]
                    )
                    # print("NEW LINE", new_l) #DEBUG
            if has_ne:
                trs_preannotated += f"{new_line}\n"
            else:
                trs_preannotated += f"{line}\n"
    with open(input_file, "w", encoding="utf-8") as f_trs:
        f_trs.write(trs_preannotated)

    return


def add_lang_tag(
    input_trs: TRSParser,
    json_dict_path: Path,
    lang_to_add: str,
):
    """
    >_ TRS in which language tags must be annotated, language tag dictionary (JSON)
    >>> TRS with new language tag annotation
    """
    try:
        dicolang = parse_json(json_dict_path)
    except FileNotFoundError:
        dicolang = {}
    output_trs = ""
    trs = open(input_trs.input_trs, "r", encoding="utf-8").read()
    trs_list = trs.split("\n")
    seen_sync = 0
    prev_nontrans = False
    prev_other_lang = False
    for line_id in range(len(trs_list)):
        line = trs_list[line_id]
        if re.search("<Sync.*", line):
            seen_sync += 1
            if seen_sync > 1 and not prev_other_lang:
                line = f'<Event desc="{lang_to_add}" type="language" extent="end"/>\n{line}'
            if "nontrans" in trs_list[line_id + 1]:
                prev_nontrans = True
            elif "<Event" and "language" in trs_list[line_id + 1]:
                prev_other_lang = True
            else:
                line = f'{line}\n<Event desc="{lang_to_add}" type="language" extent="begin"/>'
                prev_nontrans = False
                prev_other_lang = False
        elif re.search("</Turn>", line):
            seen_sync = 0
            if not prev_nontrans and not prev_other_lang:
                line = f'<Event desc="{lang_to_add}" type="language" extent="end"/>\n{line}'
        elif re.search("<Event.*", line):
            et_s = ElementTree.fromstring(line)
            if et_s.attrib["type"] == "language":
                lang_s = et_s.attrib["desc"]
                ext_s = et_s.attrib["extent"]
                if lang_s in dicolang:
                    line = f'<Event desc="{dicolang[lang_s]}" type="language" extent="{ext_s}"/>'
        output_trs += f"{line}\n"
    path_out = os.path.join(input_trs.filepath, "lang")
    os.makedirs(path_out, exist_ok=True)
    file_output = os.path.join(path_out, f"{input_trs.filename}.trs")
    with open(file_output, "w", encoding="utf-8") as f_out:
        f_out.write("".join(output_trs))

    return


## Ad hoc correction functions ---------------
def turn_difference_trs(input_trs: TRSParser):
    """
    >_ TRS for which differences in segments might be identified with its twin
    >>> Differences list
    """
    twin_trs_path = os.path.join(
        input_trs.filepath, "twins", f"{input_trs.filename}.trs"
    )
    twin_trs = TRSParser(twin_trs_path)
    print(
        f"\N{ABACUS} Searching for segmentation differences between {input_trs.filename} and {twin_trs.filename}"
    )
    for s in input_trs.contents:
        if s in [0, "NE"]:
            pass
        else:
            input_s = input_trs.contents[s]
            twin_s = twin_trs.contents[s]
            if input_s["xmin"] != twin_s["xmin"]:
                print(
                    f"Difference found in starting of segment {s} -> {input_s['xmin']} vs. {twin_s['xmin']}"
                )
            if input_s["xmax"] != twin_s["xmax"]:
                print(
                    f"Difference found in ending of segment {s} -> {input_s['xmax']} vs. {twin_s['xmax']}"
                )

    return


def trs_empty_space_before_ne(input_trs: TRSParser):
    """
    >_ TRS file in which to add an empty space before each NE
    >>> corrected TRS
    """
    output_trs = ""
    trs = open(input_trs.input_trs, "r", encoding="utf-8").read()
    trs_list = trs.split("\n")
    print(f"\N{LINKED PAPERCLIPS} Correcting {input_trs.filename}")
    for line_id in range(len(trs_list)):
        line = trs_list[line_id]
        if len(line) == 0 or re.search("<.*>", line):
            pass
        else:
            line_succ = trs_list[line_id + 1]
            line_prec = trs_list[line_id - 1]
            if re.search("<Event.*entities.*", line_succ) and re.search(
                'extent="begin"', line_succ
            ):
                line = line + " "
            if (
                re.search("<Event.*entities.*", line_prec)
                and re.search('extent="end"', line_prec)
                and line[0] not in [",", "."]
            ):
                line = " " + line
        line = line.replace("  ", " ")
        output_trs += f"{line}\n"
    path_correction = os.path.join(input_trs.filepath, "corrections", "NE")
    os.makedirs(path_correction, exist_ok=True)
    file_output = os.path.join(path_correction, f"{input_trs.filename}.trs")
    with open(file_output, "w", encoding="utf-8") as f_txt:
        f_txt.write("".join(output_trs))

    return


def correction_la(input_trs: TRSParser):
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
    txt_input = open(txt_input, "r", encoding="utf-8").read()
    txt_input = txt_input.split("\n")
    for line in txt_input:
        line_splitted = line.split(" ")
        if re.search("là", line_splitted[-1].lower()):
            nb_la += 1
            line_splitted[-1] = "la"
            line = " ".join(line_splitted)
        txt_dump += f"{line}\n"
    with open(txt_output, "w", encoding="utf-8") as f_txt:
        f_txt.write(txt_dump)
    print(f'\N{CHECK MARK} Corrected {nb_la} misplaced "là" in {input_trs.filename}')

    return


def correction_maj(input_trs: TRSParser):
    """
    >_ TRS file for correction of misplaced capital letters
    >>> corrected TRS
    """
    txt_dump, nb_maj = "", 0
    target_path = os.path.join(input_trs.filepath, "corrections", "maj")
    os.makedirs(target_path, exist_ok=True)
    trs_output = os.path.join(target_path, f"{input_trs.filename}.trs")
    txt_input = open(input_trs.input_trs, "r", encoding="utf-8").read()
    txt_input = txt_input.split("\n")
    nb_l = len(txt_input)
    for line_id in range(nb_l):
        line = txt_input[line_id]
        if re.search("<.*>", line):
            pass
        else:
            is_entity = re.search(
                'extent="begin" type="entities"', txt_input[line_id - 1]
            )
            if is_entity:
                try:
                    line = line[0].upper() + line[1:]
                    nb_maj += 1
                except IndexError:
                    pass
            elif re.search("nontrans", line):
                pass
            else:
                try:
                    line = line[0].lower() + line[1:]
                    nb_maj += 1
                except IndexError:
                    pass
        txt_dump += f"{line}\n"
    with open(trs_output, "w", encoding="utf-8") as f_out:
        f_out.write(txt_dump)
    print(
        f"\N{CHECK MARK} Corrected {nb_maj} misplaced CAPITAL in {input_trs.filename}"
    )

    return
