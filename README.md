# README

![GitHub Tag](https://img.shields.io/github/v/tag/ELDAELRA/trsproc)

*Version française plus bas*

*trsproc* is a Python module allowing multiple operations and automatic processing of TRS files from the [Transcriber](https://sourceforge.net/projects/trans/ "Download link").

Prior installation of Python 3.6+ is necessary. To install *trsproc* using pip and GitHub direct link call as follows.

```
pip install git+https://github.com/ELDAELRA/trsproc.git
```

or using git.

```
git clone https://github.com/ELDAELRA/trsproc.git
sudo python -m setup.py install
```

## USAGE

*trsproc* may be called directly from the Terminal and it will perform the specified flag on the current directory by default.

### OPTIONAL ARGUMENTS

Some optional arguments are available for advanced processing. `trsproc -flag [-option [option_argument_if_needed]]`.

* `-a` or `--audio` followed by the audio format used for the audio data corresponding to the input TRS if it is different from WAV.

* `-cl` or `--correctionlevel` followed by the number corresponding to the correction applied to the original text according to the [lexicalproc] library (https://github.com/ELDAELRA/lexicalproc):
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

---

# Version française

*trsproc* est un module Python permettant plusieurs opérations et le traitement automatique des fichiers TRS à partir du [Transcriber](https://sourceforge.net/projects/trans/ "lien de téléchargement").

Une installation préalable de Python 3.6+ est nécessaire. Pour installer *trsproc* à l'aide de pip et du lien direct GitHub, procédez comme suit.

```
pip install git+https://github.com/ELDAELRA/trsproc.git
```

ou en utilisant git.

```
git clone https://github.com/ELDAELRA/trsproc.git
sudo python -m setup.py install
```

## UTILISATION

*trsproc* peut être appelé directement depuis le terminal et il exécutera le drapeau spécifié dans le répertoire courant par défaut.

### ARGUMENTS FACULTATIFS

Certains arguments optionnels sont disponibles pour un traitement avancé. `trsproc -drapeau [-option [argument_si_besoin]]`.

* `-a` ou `--audio` suivi par le format audio utilisé pour les données audio correspondant au TRS d'entrée s'il est différent de WAV.

* `-cl` ou `--correctionlevel` suivi du chiffre corréspondant à la correction qui a été appliqué au texte d'origine selon la bibliothèque [lexicalproc](https://github.com/ELDAELRA/lexicalproc) :
  * 0, aucune correction ;
  * 1, corrections orthographiques personnalisées (_csp) ;
  * 2, corrections orthographiques automatiques (_sp) ;
  * 3, corrections grammaticales automatiques (_gram) ;
  * 12, corrections orthographiques personnalisées et automatiques (_csp_sp) ;
  * 13, corrections orthographiques personnalisées et grammaticales (_csp_gram) ;
  * 23, corrections orthographiques et grammaticales automatiques (_sp_gram) ;
  * 123, corrections orthographiques personnalisées, automatiques et grammaticales (_csp_sp_gram).

* `-f` ou `--folder` suivi d'un chemin permet de cibler le répertoire spécifié au lieu du répertoire courant.

* `-jkz` doit être spécifié si la langue à traiter dans le TRS d'entrée n'utilise pas de caractères ASCII/Latins.

* `-plh` doit être spécifié si, lors du traitement du drapeau `-txt`, seuls des fichiers txt doivent être produits.

* `-s` ou `--section` suivi du nom de section cible alternative si, lors du traitement du drapeau `-rpt` ou `-tmp`, une section différente que celle par défaut, i.e. "report", doit être ciblée.

### DRAPEAUX

En cas de drapeau incorrect, la liste des drapeaux possibles et leurs fonctions seront affichées dans la console. La même liste apparaîtra également si aucun drapeau n'est fourni.

* `-cne` supprime les annotations d'Entités Nommées si elles sont présentes dans le TRS d'entrée.

* `-crt` applique des corrections spécifiques selon la fonction choisie dans la liste proposée.
  * `turnDifferenceTRS` recherche les différences de segmentation pour le TRS d'entrée et son jumeau placé dans un sous-répertoire nommé "twin" ;
  * `trsEmptySpaceBeforeNE` ajoute un espace vide avant chaque annotation NE et enregistre le nouveau TRS dans un sous-répertoire séparé ;
  * `correctionLà` corrige les phrases se terminant par là en la. Cela nécessite l'exécution du drapeau `-txt` au préalable ;
  * `correctionMaj` corrige les majuscules mal placées.

* `-ne` extrait les annotations d'Entités Nommées si elles sont présentes dans le TRS d'entrée et les met dans un fichier tabulaire.

* `-pne` pré-annote le TRS d'entrée en utilisant le tableau créé avec le drapeau `-ne` comme un dictionnaire d'annotations personnalisé.

* `-prt` imprime le contenu du TRS parsé directement dans la console.

* `-rpt` effectue les opérations des drapeaux `-tmp` et `-vsi` afin d'obtenir les éléments de base pour la validation des données. Un rapport supplémentaire est produit avec les segments de pause de plus de 0,5s et les segments de parole de moins de 10s.

* `-rs` calcule l'échantillon minimum nécessaire à la validation de la transcription de TRS d'entrée et extrait des segments aléatoires (~~audio~~ et texte, ce dernier dans un fichier tabulaire) en fonction d'une quantité donnée.

* `-rsne` calcule l'échantillon minimum nécessaire pour la validation des Entités Nommées du TRS d'entrée et les extrait (~~audio~~ et texte, ce dernier dans un fichier tabulaire) aléatoirement selon une quantité donnée.

* `-tg` convertit le fichier TRS en fichier TextGrid.

* `-tgrs` convertit le fichier TextGrid en fichier TRS.

* `-tmp` crée un fichier TRS temporaire dans un répertoire nommé "tmp". Par défaut, ce fichier ne contiennent que la section "report" du TRS original.

* `-trs` réécrit un fichier TRS en utilisant un fichier txt d'entrée et un TRS-placeholder placé dans un sous-dossier du dossier parent d'entrée. Le TRS réécrit aura le contenu du fichier txt et la structure du TRS-placeholder.

* `-tsv` produit un fichier tabulaire avec les structures et les contenus des fichiers TRS.

* `-txt` crée des fichiers txt et TRS-placeholder. Le premier ne contenant la transcription du TRS original, le second contenant sa structure XML.

* `-vad` convertit le fichier TextGrid résultant de l'utilisation d'un algorithme de détection de l'activité vocale (VAD) en fichier TRS.

* `-vsi` produit un fichier tabulaire contenant des informations lexicales de base et des statistiques concernant le TRS d'entrée.
