# README

![GitHub Tag](https://img.shields.io/github/v/tag/ELDAELRA/trsproc)

*trsproc* is a Python module allowing multiple operations and automatic processing of TRS files from the [Transcriber](https://sourceforge.net/projects/trans/ "Download link").

Prior installation of Python 3.6+ is necessary. Install *trsproc* using pip and fork it on GitHub.

```
pip install trsproc
```

## USAGE

*trsproc* may be called directly from the Terminal and it will perform the specified flag on the current directory by default.

The class *TRSParser* may be imported in a Python for scripting pusposes using `from trsproc.parser import TRSParser`. It may be used to convert a TRS file into a Python TRSParser object retaining the transcription information in a dictionary form. 

### OPTIONAL ARGUMENTS

Some optional arguments are available for advanced processing.

```
trsproc -flag [-option [option_argument_if_needed]]
```

* `-a` or `--audio` followed by the audio format used for the audio data corresponding to the input TRS if it is different from WAV.

* `-cl` or `--correctionlevel` followed by the number corresponding to the correction applied to the original text according to the library [lexicalproc](https://github.com/ELDAELRA/lexicalproc "Work in progress"):
  * 0, no corrections;
  * 1, custom spelling corrections (_csp);
  * 2, automatic spelling corrections (_sp);
  * 3, automatic grammatical corrections (_gram);
  * 12, custom and automatic spelling corrections (_csp_sp) ;
  * 13, custom spelling and grammatical corrections (_csp_gram);
  * 23, automatic spelling and grammatical corrections (_sp_gram);
  * 123, custom spelling, automatic one and grammatical corrections (_csp_sp_gram).

* `-f` or `--folder` followed by a path allows to target the specified directory instead of the current one.

* `-jkz` must be specified if the language to be processed in the input TRS does not use ASCII/Latin based characters.

* `-plh` must be specified if the processing of the `-txt` flag must only produce txt files.

* `-s` or `--section` followed by the alternative target section name if the processing of the `-rpt` or `-tmp` flag must target a section other than the default one, i.e. "report".

### FLAGS

In case of incorrect flag the list of possible ones and their function will be printed in the console. The same list will also appear if no flag is provided. 

* `-cne` deletes the Named Entity annotations if any are present in the input TRS.

* `-crt` applies specific corrections according to the function chosen from the prompted list.
  * `turnDifferenceTRS` search for differences in segmentation for the input TRS and its twin placed in a subfolder named "twin";
  * `trsEmptySpaceBeforeNE` adds an empty space before each NE annotation and save the new TRS in a separate subfolder;
  * `correctionLà` corrects sentences ending with là in la. This needs the execution of `-txt` flag beforehand;
  * `correctionMaj` corrects misplaced capiral letters.

* `-ne` extracts the Named Entity annotations if any are present in the input TRS and put them in a tabular file.

* `-pne` pre-annotates the input TRS using the table created in the `-ne` flag as a custom annotation dictionnary.

* `-prt` print the parsed TRS contents directly in the console.

* `-rpt` performs the operations of the `-tmp` and `-vsi` flags in order to obtain the basic elements for data validation. An additional report is produced with pause segments longer than 0.5s and speech segments shorter than 10s.

* `-rs` calculates the minimum sample needed for the validation of the input TRS transcription and the extracts random segments (audio and text, the latter in a tabular file) according to a given quantity.

* `-rsne` calculates the minimum sample needed for the validation of Named Entities of the input TRS and extracts them (audio segments and text, the latter in a tabular file) randomly by a given amount.

* `-tg` converts TRS files to TextGrid files.

* `-tgrs` converts TextGrid files to TRS files.

* `-tmp` creates TRS-temporary files in a directory named "tmp". By default, these files contain only the "report" section(s) of the original TRS.

* `-trs` rewrites a TRS file using the input txt file and a TRS-placeholder placed in a subfolder of the parent input folder. The rewritten TRS will have the content of the txt and the structure of the TRS-placeholder.

* `-tsv` produces a tabular file from with the structures and contents of the TRS files.

* `-txt` creates txt and TRS-placeholder files. The first only containing the transcription of the original TRS, the latter having its XML structure.

* `-vad` converts TextGrid files resulting from the use of a voice activity detection algorithm (VAD) into TRS files.

* `-vsi` produces a tabular file containing basic lexical information and statistics concerning the input TRS.

### TRSParser class

When the class is initiated only the TRS file path must be provided. parameters `audio_format` and `lang` may be modified from their default values if needed. `audio_format` defaults to `'wav'` and is used to find an audio file with the same name and location of the TRS. `lang` defaults to `'eu'` and is used This is mainly used for word count in the transcription and can be changed to `'jkz'` in order to process a character count instead based on UNICODE characters.  

#### Attributes

* `tree` is the parsed XML tree.

* `root` is the root of the parsed XML tree.

* `inputTRS` is the complete path to the parsed TRS file.

* `filepath` is the path to the folder of the parsed TRS file.

* `corpus` is the name of the folder where the TRS file is located.

* `filename` is the name of the parsed TRS file.

* `lang` refers to the lang parameter from the TRSParser call.

* `sectionduration` represents the sum of the duration of all the sections present in the TRS file. Returns 'Section not found' value if there is no section tag in the TRS file.

* `fileduration` represents the duration of an audio file having the same name and location of the TRS. Returns 'audio not found' value if it fails to find an audio file.

* `speakers` is a Python dictionary containing the speakers' information provided in the TRS header if any. The speaker's id is used as key, the value is a tuple of speaker's name and sex.
        
* `contents` is a Python dictionary containing all the information about the TRS' segments and the overall transcription.
  * `contents[n]` represents a segment where n is its rank in the transcription. Each segment has seven keys:
    * `contents[n]['xmin']` is the segment starting point in seconds.
    * `contents[n]['xmax']` is the segment ending point in seconds.
    * `contents[n]['duration']` is the segment duration in seconds.
    * `contents[n]['tokens']` is the number of tokens present in the segment.
    * `contents[n]['content']` is the segment transcription.
    * `contents[n]['speaker']` is the segment speaker if any.
    * `contents[n]['SNR']` is the Signal-to-noise ratio of the segment. It returns `'NA'` if the SNR computation fails.
  * `contents['NE']` is a dictionary of all the Named Entities present in the TRS if any.  
    * `contents['NE'][n]` represents a Named Entity entry where n is its rank in the transcription. Each NE has four keys:
    * `contents['NE'][n]['class']` is the Named Entity class.
    * `contents['NE'][n]['xmin']` is the Named Entity starting point in seconds.
    * `contents['NE'][n]['segmentID']` is the id of the segment where the Named Entity has been annotated.
    * `contents['NE'][n]['content']` is the transcription associated with the Named Entity.

  * `contents[0]` contains overall statistics about the TRS file.
    * `contents[0]['totalSegments']` returns the total number of segments in the TRS.
    * `contents[0]['totalWords']` returns the total number of word (separated by a white space in case of `lang='eu'`. It returns the total number of UNICODE characters in case of `lang='jkz'`
    * `contents[0]['totalNE']` returns the total number of Named Entities in the TRS if any.
    * `contents[0]['totalNonTrans']` returns the total number of nontrans tags in the TRS if any.
    * `contents[0]['totalPronPi']` returns the total number of pi tags in the TRS if any.
    * `contents[0]['totalTrans']` returns the total number of segments having an actual transcription.
    * `contents[0]['totalLang']` returns the total number of language tags in the TRS if any.
    * `contents[0]['otherLang']` contains a list of the different languages annotated in the TRS.
    * `contents[0]['duration']` returns the total duration of the segments having transcription, pi and nontrans annotations.
    * `contents[0]['durationTrans']` returns the duration of the transcribed segments.
    * `contents[0]['durationNonTrans']` returns the duration of the nontrans segments.
    * `contents[0]['durationPronPi']` returns the duration of the pi segments.
    * `contents[0]['meanSNR']` returns the mean SNR of the audio file or `'NA'` if it fails to compute it.
    
#### Functions

Coming soon.