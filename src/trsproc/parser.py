#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
##
### TRS parsing class
#### trsproc.py dependency
#####

"""
def addLangTag(self):
    dicolang = importJSON ?
    output_trs, lang_open, lang_close = "", 0, 0
    trs = open(self.inputTRS, 'r', encoding).read()
    trs_list = trs.split("\n)
    for i in range(len(trs_list)):
    l = trs_list[i]
        if re.search("<Event.*", l)
            et_s = ElementTree.fromstring(l)
            if et_s.attrib['type'] == "language"
                lang_s = et_s.attrib['desc]
                ext_s = et_s.attrib['extent]
                l = f'<Event desc="{dicolang[lang_s]}" type="language" extent="{ext_s}"/>'
        elif re.search("<Sync.*, l) and lang_open == lang_close:
            if trs_list[i+1] != ""
                l =f'{l}\n<Event desc="*langtoadd*" type="language" extent="begin"/>'
                lang_open += 1
            elif re.seach("<Event.*, trs_list[i+2]):
                et_s = ElementTree.fromstring(trs_list[i+2])
                if et_s.attrib['type'] in ["entities, pronounce]:
                    l =f'{l}\n<Event desc="*langtoadd*" type="language" extent="begin"/>'
                    lang_open += 1
        elif re.search("</Turn.*, l) and lang_open-langclose == 1:
            l=f'<Event desc="*langtoadd*" type="language" extent="end"/>\n{l}'
            lang_close +=1
        output_trs += f"{l}\n"
    if lang_open != lang_close:
        print(f'{lang_open} open tags vs. {lang_close} closing tags)
    path_out = os.path.join(self.filepath, "lang")
    os.makedirs(path_out, exist_ok=True)
    file_output = os.path.join(path, f"{self.filename}.trs")
    with open(file_output, 'w', encoding) as f_out:
    f_out.write(""join(output_trs))
    return

def sanityCheckLangTag(self)
    trs = open(self.inputTRS).read()
    trs_list = trs.split("\n)
    lang_tag = ("none, 0)
    for i in range(len(trs_list))
        l = trs_list[i]
        if re.search("<Event.*", l)
            et_s = ElementTree.fromstring(l)
            if et_s.attrib['type'] == "language"
                if et_s.attrib['extent'] == "begin"
                    if lang_tag[0] == "open:
                        print(f"!!! second open tag at line {i} after {lang_tag[1]})
                    else:
                        lang_open = ("open", i)
                if et_s.attrib['extent'] == "end"
                    if lang_close[0] == "closed:
                        print(f"!!! second closing tag at line {i} after {lang_tag[1]})
                    else:
                        lang_tag = ("closed", i)
    
    return

"""
# Global imports
import os, re
import parselmouth, textgrids
from xml.etree import cElementTree as ElementTree
from xml.etree.ElementTree import ParseError

#----------
def replacingPunctuations(sentence):
    """
    >_ sentence to delete punctuation from
    >>> original sentence without punctuation
    """
    sentence = sentence.strip()
    punct_list = ["\ufeff", "\u00A0", "\u2019", ".", ":", ";", "!", '"', "/", "\\", "%", "'"]
    for t in punct_list:
        sentence = sentence.replace(t, "")

    return sentence


def praatSNRforSegment(audio, seg_start, seg_end):
    """
    >_audio file, timestaps for start and end of segment
    >>> segment SNR from Praat HNR computation
    """
    sound = parselmouth.Sound(audio)
    sound_part = sound.extract_part(seg_start, seg_end)
    # superimposed speech 20 < SNR > 45
    hnr = sound_part.to_harmonicity()
    mean_snr = parselmouth.praat.call(hnr, "Get mean", 0, 0)

    return round(mean_snr, 2)


class TRSParser():
    def __init__(self, trs_in, audio_format='wav', lang='eu'):
        tree = ElementTree.parse(trs_in)
        root = tree.getroot()

        self.inputTRS = trs_in
        self.filepath, self.filename = os.path.split(trs_in)
        self.filename = self.filename.split(".")[0]
        self.corpus = os.path.basename(self.filepath)
        self.lang = lang

        try:
            self.sectionduration = []
            for sec in root.iter('Section'):
                self.sectionduration.append(round(float(sec.attrib['endTime'])-float(sec.attrib['startTime']), 3))
            self.sectionduration = sum(self.sectionduration)
        except ValueError:
            self.sectionduration = 'Section not found'
        try:
            self.audiofile = os.path.join(self.filepath, f'{self.filename}.{audio_format}')
            self.fileduration = round(parselmouth.Sound(self.audiofile).duration, 3)
        except parselmouth.PraatError:
            self.fileduration = 'audio not found'

        self.speakers = {}
         ## Retrieve speakers information when present in header of TRS
        for spks in root.iter('Speaker'):
            spk_id = spks.attrib['id']
            if "type" in spks.attrib:
                spk_sex = spks.attrib['type']
            else:
                spk_sex = ""
            self.speakers[spk_id] = (spks.attrib['name'], spk_sex)
        
        self.contents = self.retrieveContents()
    

    def retrieveContents(self):
        """
        >_ TRS file to be parsed for information retrieving
        >>> Dictionary of all contents information
        """
        seg_dict, seg_id, seg_start, seg_end = {}, 0, 0, 0
        nb_nontrans, nb_pronpi, nb_lang, nb_words = 0, 0, 0, 0
        dur_trans, dur_nontrans, dur_pronpi, dur_other_lang = 0, 0, 0, 0
        langs = []
        turn_id, turn_end = 0, 0
        ne_dict, ne_id = {}, 0
        trs = open(self.inputTRS, encoding='utf-8').read()
        trs_list = trs.split("\n")
        for i in range(len(trs_list)):
            l = trs_list[i]
            if re.search("<Turn.*>", l):
             # Turn info is not stored, only used for segment end times and speakers
                turn_trans = ""
                turn_trans = l
                turn_id += 1
                for t in trs_list[i+1:]:
                    if t == "</Turn>":
                        turn_trans += t
                        break
                    else:
                        turn_trans += t
                et_turn = ElementTree.fromstring(turn_trans)
                turn_end = float(et_turn.attrib['endTime'])
                try:
                    turn_spk = et_turn.attrib['speaker']
                except KeyError:
                    turn_spk = 'NA'
                #print(f'TURN {turn_id} from {turn_start} to {turn_end}') ### DEBUG
            elif re.search("<Sync.*>", l):
             # Segment info retrieved starting here
                seg_id += 1
                seg_trans = ''
                seg_line = ElementTree.fromstring(l) #Acces attributes of a line as in root
                seg_dict[seg_id] = {}
                seg_start = float(seg_line.attrib['time'])
                for s_id in range(i+1, len(trs_list)):
                    s = trs_list[s_id]
                    if re.search("<Sync.*>", s):
                        seg_end = float(ElementTree.fromstring(s).attrib['time'])
                        break
                    elif s == "</Turn>":
                        seg_end = float(turn_end)
                        break    
                    elif re.search('<Event.*', s):
                        try:
                            et_s = ElementTree.fromstring(s)
                            if et_s.attrib['desc'] == "nontrans":
                                seg_trans = "[nontrans]"
                            elif et_s.attrib['desc'] == "pi":
                                seg_trans = "[pronpi]"
                            if et_s.attrib['type'] == "language":
                                nb_lang += 1
                                lang_oth = et_s.attrib['desc']
                                langs.append(lang_oth)
                                seg_trans = f'[lang={lang_oth}]'
                            elif et_s.attrib['type'] == "entities" and et_s.attrib['extent'] == "begin":
                                ne_id += 1
                                ne_dict[ne_id] = {}
                                ne_dict[ne_id]['class'] = et_s.attrib['desc']
                                ne_dict[ne_id]['xmin'] = seg_start
                                ne_dict[ne_id]['segmentID'] = seg_id
                                ne_dict[ne_id]['content'] = trs_list[s_id+1]
                        except ParseError:
                            pass
                    else:
                        seg_trans += s+"\n"
                seg_trans = seg_trans.rstrip("\n")
                seg_tokens = len(seg_trans.strip().split(" "))
                if self.lang == "jkz":
                    for st in seg_trans:
                        seg_tokens += len(st)
                else:
                    seg_tokens += len(seg_trans.split("'"))-1
                seg_dur = round(seg_end-seg_start, 3)
                #print(f"!!! SEGMENT {seg_id} from {seg_start} to {seg_end} = {seg_trans}") ### DEBUG
                seg_dict[seg_id]['xmin'] = seg_start
                seg_dict[seg_id]['xmax'] = seg_end
                seg_dict[seg_id]['duration'] = seg_dur
                seg_dict[seg_id]['tokens'] = seg_tokens
                seg_dict[seg_id]['content'] = seg_trans.replace('\n', '')
                seg_dict[seg_id]['speaker'] = turn_spk
                try:
                    seg_dict[seg_id]['SNR'] = praatSNRforSegment(self.audiofile, seg_start, seg_end)
                except parselmouth.PraatError:
                    seg_dict[seg_id]['SNR'] = 'NA'
        #print(f'Total SEGMENTS {seg_dict}') ### DEBUG
        #print(f'\tTotal NE {ne_dict}') ### DEBUG
        for x in seg_dict:
            if x not in ['NE', 0]:
                if seg_dict[x]['content'] in ["", '[nontrans]']:
                    dur_nontrans += seg_dict[x]['duration']
                    nb_nontrans += 1
                elif seg_dict[x]['content'] == '[pronpi]':
                    dur_pronpi += seg_dict[x]['duration']
                    nb_pronpi += 1
                elif re.search("lang=", seg_dict[x]['content']):
                    dur_other_lang += seg_dict[x]['duration']
                else:
                    nb_words += seg_dict[x]['tokens']
                    dur_trans += seg_dict[x]['duration']
        seg_dict['NE'] = ne_dict
        seg_dict[0] = {}
        seg_dict[0]['totalSegments'] = seg_id
        seg_dict[0]['totalWords'] = nb_words
        seg_dict[0]['totalNE'] = ne_id
        seg_dict[0]['totalNonTrans'] = nb_nontrans
        seg_dict[0]['totalPronPi'] = nb_pronpi
        seg_dict[0]['totalTrans'] = seg_id-(nb_nontrans+nb_pronpi)
        seg_dict[0]['totalLang'] = nb_lang
        seg_dict[0]['otherLang'] = set(langs)
        seg_dict[0]['duration'] = round(dur_trans+dur_nontrans+dur_pronpi, 3)
        seg_dict[0]['durationTrans'] = round(dur_trans, 3)
        seg_dict[0]['durationNonTrans'] = round(dur_nontrans, 3)
        seg_dict[0]['durationPronPi'] = round(dur_pronpi, 3)
        try:
            seg_dict[0]['meanSNR'] = praatSNRforSegment(self.audiofile, 0, self.fileduration)
        except parselmouth.PraatError:
            seg_dict[0]['meanSNR'] = 'NA'

        return seg_dict


    def print(self):
        """
        >>> print TRS contents in the console
        """
        print(f"{self.filename} with section duration {self.sectionduration} and audio duration {self.fileduration} in\n{self.filepath}\nSPEAKERS ====================\n{self.speakers}\nCONTENTS ====================\n{self.contents}")
    
        return


    def summaryLangTRS(self):
        """
        >_ TRS file
        >>> tsv with information about the languages spoken in the TRS
        """
        tab_out = os.path.join(self.filepath, f"summary_languages-{self.corpus}.tsv")
        print(f"\N{CARD FILE BOX} Retriveving languages from {self.filename}")
        try:
            open(tab_out).close()
        except FileNotFoundError:
            with open(tab_out, 'w', encoding='utf-8') as f:
                f.wirte("file_name\tfile_path\tdur_tot\tdur_trans\tnb_seg\tnb_lang\tlanguage\tseg_id\tseg_start\tseg_end\tseg_dur")
        with open(tab_out, 'a', encoding='utf-8') as f:
            for s in self.contents:
                if s not in ['NE', 0] and re.search(self[s]['content']):
                    f.write(f"\n{self.filename}\t{self.filepath}\t{self.fileduration}\t{self.contents[0]['durationTrans']}\t{self.contents[s]['totalsegments']}\t{self.contents[0]['totalLang']}\t{self.contents[s]['content']}\t{s}\t{self.contents[s]['xmin']}\t{self.contents[s]['xmax']}\t{self.contents[s]['duration']}")
        
        return


    def trsToTxt(self, need_placeholder=True):
        """
        >_ TRS file 
        >>> txt file having transcribed text
        >>> if need_placeholder=True, trs with [placeholder x] where x = index from the txt list for TRS rewriting
        """
        print(f"\N{LINKED PAPERCLIPS} Processing {self.filename}...")
        output_txt, output_trs_plh, placeholder = "", "", 0
        trs = open(self.inputTRS, encoding='utf-8').read()
        trs_list = trs.split("\n")
        for l in trs_list:
            if len(l) == 0 or re.search("<.*>", l):
                output_trs_plh += f"{l}\n"
            else:
                 ### Character entities representation correction and deletion of punctuation
                l = replacingPunctuations(l)
                if placeholder == 0:
                    output_txt += l
                else:
                    output_txt += f"\n{l}"
                output_trs_plh += f"[placeholder {placeholder}]\n"
                placeholder += 1
        if need_placeholder:
            path_placeholders = os.path.join(self.filepath, "placeholder")
            file_placeholder = os.path.join(path_placeholders, f"{self.filename}_placeholder.trs")
            os.makedirs(path_placeholders, exist_ok=True)
            with open(file_placeholder, 'w', encoding='utf-8') as f_plh_trs:
                    f_plh_trs.write("".join(output_trs_plh))
        path_txts = os.path.join(self.filepath, "txt")
        os.makedirs(path_txts, exist_ok=True)
        file_output = os.path.join(path_txts, f"{self.filename}.txt")
        with open(file_output, 'w', encoding='utf-8') as f_txt:
            f_txt.write("".join(output_txt))
    
        return


    def txtToTrs(input_txt, from_correction=0):
        """
        >_ txt file having the transcription to be rewritten in a TRS, one segment per line and line length = last placeholder
        >>> rewritten TRS, from_correction parameter helps to identify the file name
        """
        output_trs_correct = ""
        txt_path, txt_name = os.path.split(input_txt)
        txt_name = txt_name.split(".")[0]
        txt_folder = os.path.basename(txt_path)
        origin_path = txt_path.rstrip(txt_folder)
        correction_level = {0:"", 1:"_csp", 2:"_sp", 3:"_gram", 12:"_csp_sp", 13:"_csp_gram", 23:"_sp_gram", 123:"_csp_sp_gram"}
     ## find the correct text to rewrite
        if from_correction != 0:
            corrected_folder = os.path.join(txt_path, "corrections", "corrected")
            os.makedirs(corrected_folder, exist_ok=True)
            correction_folder = correction_level[from_correction].split("_")[-1]
            txt_input = os.path.join(txt_path, "corrections", correction_folder, f"{txt_name}{correction_level[from_correction]}.txt")
            trs_output = os.path.join(corrected_folder, f"{txt_name}{correction_level[from_correction]}.trs")
        else:
            txt_input = os.path.join(txt_path, f"{txt_name}.txt")
            trs_output = os.path.join(txt_path, f"{txt_name}.trs")
     ## seach for the TRS placeholder
        trs_placeholder = os.path.join(origin_path, "placeholder", f"{txt_name}_placeholder.trs")
        trs_input = open(trs_placeholder, encoding='utf-8').read()
        trs_list = trs_input.split("\n")
        txt_input = open(txt_input, encoding='utf-8').read()
        txt_list = txt_input.split("\n")
        print(f"\N{PACKAGE} Re-writing {txt_name}...")
        for l in trs_list:
            if len(l) == 0 or re.search("<.*>", l):
                output_trs_correct += f"{l}\n"
             ## writing TRS original XML structure into
            elif re.search("[placeholder .+]", l):
                plh = l.split(" ")[1]
                plh = int(plh.rstrip("]"))
                output_trs_correct += f"{txt_list[plh]}\n"
             ## adding new txt content
        with open(trs_output, 'w', encoding='utf-8') as f_trs:
            f_trs.write("".join(output_trs_correct))

        return


    def cleanNEfromTRS(self):
        """
        >_ TRS file transcribed and annotated to NE
        >>> TRS file without NE annotations
        """
        txt_path, file_name = self.filepath, self.filename
        cleaned_folder = os.path.join(txt_path, "clean")
        os.makedirs(cleaned_folder, exist_ok=True)
        file_name = file_name.replace("_EN", "")
        trs_output = os.path.join(cleaned_folder, f"{file_name}.trs")
        trs_input = open(self.inputTRS, encoding='utf-8').read()
        trs_list = trs_input.split("\n")
        output_trs_cleaned = trs_list[0]
        print(f"\N{PACKAGE} Cleaning {file_name}...")
        for i in range(1, len(trs_list)):
            l = trs_list[i]
            if re.search("<.*>", l):
                if re.search("<Event.*entities.*", l):
                    try:
                        last_char_trans_prec = trs_list[i-1][-1]
                        if last_char_trans_prec not in [" ", "'", "-", "_"]:
                            output_trs_cleaned += " "
                    except IndexError:
                        pass
                elif re.search("<Sync.*", l):
                    output_trs_cleaned += f"\n{l}\n"
                else:
                    output_trs_cleaned += f"\n{l}"
            else:
                output_trs_cleaned += f"{l}"
     ## cleaning transcriptions from NE annotation white space
        output_trs_cleaned = output_trs_cleaned.replace("  ", " ")
        output_trs_cleaned = output_trs_cleaned.replace(" ,", ",")
        output_trs_cleaned = output_trs_cleaned.replace(" .", ".")
        with open(trs_output, 'w', encoding='utf-8') as f_trs:
            f_trs.write("".join(output_trs_cleaned))

        return


    def validateTRS(self):
        """
        >_ TRS for infrmation extraction
        >>> validation table with technical info about TRS
        """
        tab_out = os.path.join(self.filepath, f"summary_validation-{self.corpus}.tsv")
        print(f"\N{CARD FILE BOX} Retrieving information from {self.filename}...")
        try:
            open(tab_out).close()
        except FileNotFoundError:
         ## create a header if the table does not exist
            with open(tab_out, 'w', encoding='utf-8') as f:
                f.write("file_name\tfile_path\tnb_spk\tnb_lang\tdur_tot\tdur_trans\tdur_nontrans\tdur_pronpi\tnb_seg\tnb_trans\tnb_nontrans\tnb_pronpi\tnb_words\tnb_NE")
        with open(tab_out, 'a', encoding='utf-8') as f_tsv:
            f_tsv.write(f"\n{self.filename}\t{self.filepath}\t{len(self.speakers)}\t{len(self.contents[0]['oterhLang'])+1}\t{self.fileduration}\t{self.contents[0]['durationTrans']}\t{self.contents[0]['durationNonTrans']}\t{self.contents[0]['durationPronPi']}\t{self.contents[0]['totalSegments']}\t{self.contents[0]['totalTrans']}\t{self.contents[0]['totalNonTrans']}\t{self.contents[0]['totalPronPi']}\t{self.contents[0]['totalWords']}\t{self.contents[0]['totalNE']}")
    
        return 


    def trsToTsv(self):
        """
        >_ TRS file 
        >>> tsv file representing the origin TRS
        """
        tab_out = os.path.join(self.filepath, f"{self.corpus}.tsv")
        print(f"\N{CARD FILE BOX} Creating tsv from {self.filename}...")
        try:
            open(tab_out).close()
        except FileNotFoundError:
         ## create a header if the table does not exist
            with open(tab_out, 'w', encoding='utf-8') as f:
                f.write("file_name\tfile_path\tsegment\tsegment_start\tsegment_end\tsegment_duration\ttranscription\tspeaker\tspeaker_sex")
        with open(tab_out, 'a', encoding='utf-8') as f_tsv:
            for s in self.contents:
                if s not in ['NE', 0]:
                    f_tsv.write(f"\n{self.filename}\t{self.filepath}\t{s}\t{self.contents[s]['xmin']}\t{self.contents[s]['xmax']}\t{self.contents[s]['duration']}\t{self.contents[s]['content']}\t")
                    try:
                        f_tsv.write("\t".join(self.speakers[self.contents[s]['speaker']]))
                    except KeyError:
                        f_tsv.write("NA\tNA")
    
        return 


    def vadToTRS(input_tg):
        """
        >_ TextGrid file with Tier named VAD
        >>> TRS file
        """
        tg_path, tg_name = os.path.split(input_tg)
        tg_name = tg_name.split(".")[0]
        print(f"\N{MOUTH} Writing TRS from tg {tg_name}...")
        grid = textgrids.TextGrid(input_tg)
     ## Create textgrid object from input file
        grid_xmax = round(grid["VAD"][-1].xmax, 3)
     ## Retrieve total duration of file
        trs_preamble = f'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE Trans SYSTEM "trans-14.dtd">\n<Trans scribe="" audio_filename="{tg_name}" version="4" version_date="">\n'
        trs_preamble_spk = '<Speakers>\n<Speaker id="spk1" name="a transcrire"/>\n'
        trs_corps = ''
        trs_closure = '</Section>\n</Episode>\n</Trans>'
     ## Create TRS preambule, body (starting empty) and conclusion texts
        trs_preamble_spk += f'</Speakers>\n<Episode>\n<Section type="report" startTime="0" endTime="{grid_xmax}">\n'
        for i in grid["VAD"]:
         ## Loop on transcription Tier to retrieve info and write in formatted TRS text
            transcription, t_min, t_max = i.text, round(i.xmin, 3), round(i.xmax, 3)
            if transcription == "speech":
                trs_corps += f'<Turn speaker="spk1" startTime="{t_min}" endTime="{t_max}">\n<Sync time="{t_min}"/>\n\n</Turn>\n'
            else:
                trs_corps += f'<Turn startTime="{t_min}" endTime="{t_max}">\n<Sync time="{t_min}"/>\n\n<Event desc="nontrans" type="noise" extent="instantaneous"/>\n\n</Turn>\n'
        dump_trs = trs_preamble + trs_preamble_spk + trs_corps + trs_closure
        with open(os.path.join(tg_path, f"{tg_name}.trs"), 'w', encoding='utf-8') as f:
            f.write(dump_trs)

        return


    def trsToTextGrid(self, tiers_list=['transcription', 'speaker', 'sex', 'NE']):
        """
        >_ TRS file 
        >>> TextGrid file
        """
        tg_out = os.path.join(self.filepath, f"{self.filename}.TextGrid")
        nb_tiers = len(tiers_list)
        nb_intervals = self.contents[0]['total']
        with open(tg_out, 'w', encoding='utf-8') as tg:
            tg.write(f'File type = "ooTextFile"\nObject class = "TextGrid"\n\nxmin = 0\nxmax = {self.fileduration}\ntiers? <exists>\nsize = {nb_tiers}\nitem []:')
            for tier_name in tiers_list:
                tier_index = tiers_list.index(tier_name)+1
                tg.write(f'\n\titem [{tier_index}]:\n\t\tclass = "IntervalTier"\n\t\tname = "{tier_name}"\n\t\txmin = 0\n\t\txmax = {self.fileduration}\n\t\tintervals: size = {nb_intervals}')
                for i in self.contents:
                    if i not in ['NE', 0]:
                        seg_st, seg_en = self.contents[i]['xmin'], self.contents[i]['xmax']
                        tg.write(f'\n\t\tintervals [{i}]:\n\t\t\txmin = {seg_st}\n\t\t\txmax = {seg_en}\n\t\t\ttext = "')
                        if tier_name == "transcription":
                            tg.write(f'{self.contents[i]["content"]}"')
                        elif tier_name == "speaker":
                            try:
                                spk_name = self.speakers[self.contents[i]['speaker']][0]
                            except KeyError:
                                spk_name = ""
                            tg.write(f'{spk_name}"')
                        elif tier_name == "sex":
                            try:
                                spk_sex = self.speakers[self.contents[i]['speaker']][1]
                            except KeyError:
                                spk_sex = ""
                            tg.write(f'{spk_sex}"')
                        elif tier_name == "NE":
                            ne_content = ""
                            for ne in self.contents['NE']:
                                if self.contents['NE'][ne]['segmentID'] == i:
                                    ne_content += f"{self.contents['NE'][ne]['class']}:{self.contents['NE'][ne]['content']}_"
                            tg.write(f'{ne_content.strip()}"')
                        else:
                            tg.write("")

        return


    def textGridToTRS(input_tg):
        """
        >_ fichier TextGri
        >>> TRS formatté selon specs du projet ELDA-0773
        """
        tg_path, tg_name = os.path.split(input_tg)
        tg_name = tg_name.split(".")[0]
        trans = os.path.basename(tg_path)
        grid = textgrids.TextGrid(input_tg)
     ## Create textgrid object from input file
        print(f"\N{PACKAGE} Writing TRS from tg {tg_name}...")
        grid_xmax = grid["transcription"][-1].xmax
        trs_preamble = f'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE Trans SYSTEM "trans-14.dtd">\n<Trans scribe="{trans}" audio_filename="{tg_name}" version="4" version_date="">\n'
        trs_preamble_spk = '<Speakers>\n'
        trs_corps = ''
        trs_closure = '</Section>\n</Episode>\n</Trans>'
     ## Create TRS preambule, body (starting empty) and conclusion texts
        nb_int = len(grid['speaker'])
        spk_sex_tuple_list = []
        for x in range(nb_int):
     ## analyse the speaker and sexe Tiers to retrieve speakers info and write them in preambule
            spk_sex_tuple_list.append((grid["speaker"][x].text, grid["sexe"][x].text))
     ##### CHANGE TO DICT for better looping
     ##### { spk_id:(name, type)}
        spk_sex_tuple_list = set(spk_sex_tuple_list)
        spk_sex_dict = {}
        for i in spk_sex_tuple_list:
            spk_id = 1
            spk_sex_dict[i[0]] = f"spk{spk_id}"
            if i[0] != "":
                trs_preamble_spk += f'<Speaker id="spk{spk_id}" name="{i[0]}" check="no" type="{i[1]}"/>\n'
                spk_id += 1
        trs_preamble_spk += f'</Speakers>\n<Episode>\n<Section type="report" startTime="0" endTime="{grid_xmax}">\n'
        for t in range(nb_int):
         ## Loop on transcription Tier to retrieve info and write in formatted TRS text
            transcription, t_min, t_max, t_spk = grid["transcription"][t].text, grid["transcription"][t].xmin, grid["transcription"][t].xmax, grid["speaker"][t].text
            t_spk = spk_sex_dict[t_spk]
            if transcription == "":
                trs_corps += f'<Turn startTime="{t_min}" endTime="{t_max}">\n<Sync time="{t_min}"/>\n\n<Event desc="nontrans" type="noise" extent="instantaneous"/>\n\n</Turn>\n'
            else:
                trs_corps += f'<Turn speaker="{t_spk}" startTime="{t_min}" endTime="{t_max}">\n<Sync time="{t_min}"/>\n{transcription}\n</Turn>\n'
        dump_trs = trs_preamble + trs_preamble_spk + trs_corps + trs_closure
        with open(os.path.join(tg_path, f"{tg_name}.trs"), 'w', encoding='utf-8') as f:
            f.write(dump_trs)

        return 


    def retrieveNEToTsv(self):
        """
        >_ TRS file with NE annotation
        >>> tsv with NE annotation information
        """
        tab_out = os.path.join(self.filepath, f"{self.corpus}_NE_extraction.tsv")
        print(f"\N{CARD FILE BOX} Retrieving NE from {self.filename}...")
        try:
            open(tab_out).close()
        except FileNotFoundError:
         ## create a header if the table does not exist
            with open(tab_out, 'w', encoding='utf-8') as f:
                f.write("file_name\tfile_path\tNE_rank\tNE_class\tNE_content\tsegment_rank\tsegment_content\tsegment_start\tsegment_end\tsegment_duration\tspeaker\tspeaker_sex")
        with open(tab_out, 'a', encoding='utf-8') as f_tsv:
            for ne in self.contents['NE']:
                ne_info = self.contents['NE'][ne]
                s = ne_info['segmentID']
                try:
                    ne_spk = "\t".join(self.speakers[self.contents[s]['speaker']])
                except KeyError:
                    ne_spk = "NA\tNA"
                    
                f_tsv.write(f"\n{self.filename}\t{self.filepath}\t{ne}\t{ne_info['class']}\t{ne_info['content']}\t{s}\t{self.contents[s]['content']}\t{self.contents[s]['xmin']}\t{self.contents[s]['xmax']}\t{self.contents[s]['duration']}\t{ne_spk}")

        return 


    def trsTMP(self, section_type="report"):
        """
        >_ TRS file with specific section to be extracted
        >>> temporary TRS only retaining the target section
        """
        print(f"\N{BULLSEYE} Extracting '{section_type}' Section from {self.filename}...")
        file_tmp_list, nb_target = [], 0
        path_tmp = os.path.join(self.filepath, "tmp")
        os.makedirs(path_tmp, exist_ok=True)
        trs = open(self.inputTRS, encoding='utf-8').read()
        trs_list = trs.split("\n")
        for l in trs_list:
            if re.search("<Section.*>", l):
                section_txt = l
                s_id = trs_list.index(l)
                for s in trs_list[s_id+1:]:
                    section_txt += f'\n{s}'
                    if re.search("</Section>", s):break
                et_section = ElementTree.fromstring(section_txt)
                try:
                    sectionType = et_section.attrib['type']
                    if sectionType == section_type:
                        nb_target += 1
                        file_tmp = os.path.join(path_tmp, f"{self.filename}.{section_type}_{nb_target}.trs")
                        file_tmp_list.append(file_tmp)
                        with open(file_tmp, 'w', encoding='utf-8') as f_tmp_trs:
                            f_tmp_trs.write("".join(section_txt))
                except KeyError:
                    pass

        return file_tmp_list
