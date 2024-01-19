# README

---

Le script *trsproc* permet d'effecuer des traitements divers avec des fichiers au format TRS. Il est possible de lancer le script en ligne de commande, au préalable il faudra avoir une installation Python 3.6+ ainsi que les libraries listées dans le fichier requirements.txt (pip install -r requirements.txt).

Si la langue des TRS à traiter est une langue asiatique, autour de la ligne 67 de *trsproc.py* devra figurer "ff = TRSParser(d, lang='jkz')".

Son utilisation idéale est la suivante :
1. Lancer un terminal et se placer dans le répertoire dans lequel l'on souhaite que les fichiers soient traités,
	ex. cd /Users/user/data

2. Appeler *trsproc* depuis son chemin absolu avec le flag adapté au traitement souhaité,
	ex. python /Users/user/trsproc/trsproc.py -flag

En cas de mauvais flag une liste avec les différentes possibilités sera affichée.

**NB** Toutes les phases de l'algorithme peuvent être lancé en ciblant un répertoire spécifique en le passant comme deuxième argument 
ex. python3 path/to/trsproc/trsproc.py -flag /path/to/specific/folder (non recommandé)

## Les flags possibles

-cne : effectue l'effacement de l'annotation en Entités Nommées présente dans les TRS en entrée.

-crt : applique des corrections spécifiques selon la fonction présente autour de la ligne 30 de *trsproc.py* et importée par défaut de *utils_trsproc.py*. Changer le nom de cette fonction selon la correction souhaitée.

-ne : permet l'extraction des entités nommées présentes dans les TRS en entrée sous forme de tableau.

-pne : effectue une pré-annotation des TRS en entrée à partir du tableau créé en utilisant le flag -ne.

-rpt : permet d'effectuer les opération du flag tmp et vsi afin d'obtenir des éléments de base pour la validation de données du projet 0774.

-rs : permet d'effectuer un calcul de l'échantillon minimum pour la validation de transcription en TRS et l'extraction de segments aléatoires selon une quantité donnée.

-rsne : permet d'effectuer un calcul de l'échantillon minimum pour la validation d'entités nommées en TRS et leur extraction aléatoire selon une quantité donnée.

-tg : permet la conversion de fichiers TRS à fichiers TextGrid.

-tgrs : permet la conversion de fichiers TextGrid à fichiers TRS.

-tmp : permet la création de fichiers TRS-temporaire dans un répertoire nommé "tmp". Par défaut ces fichiers contiennent uniquement la ou les sections "report" du TRS d'origine.
**NB** Pour cibler une Section différente, autour de la ligne 69 de *trsproc.py* devra figurer "fun(ff, section_type='sectionCible')".

-trs : prend en entrée un dossier avec des fichiers txt et recherche des fichiers TRS-placeholder dans le dossier parent pour effectuer une réecriture de TRS à partir du contenu des fichiers txt.

-tsv : produit un fichier tabulaire (tsv) avec les structures et contenus des TRS et portant le nom du dossier dans lequel sont présents les fichiers traités.

-txt : permet la création de fichiers txt et TRS-placeholder. Le premier contient uniquement la transcription des TRS d'origine alors que le deuxième contient uniquement sa structure et sera utilisé pour la réecriture en cas de corrections à appliquer dans les txt ou autre opération similaire.
**NB** Si l'on souhaite produire uniquement les txt, autour de la ligne 69 de *trsproc.py* devra figurer "fun(ff, False)".

-vad : permet la conversion de fichiers TextGrid issus de l'utilisation d'un algorithme de détection d'activité vocale (VAD) en fichiers TRS.

-vsi : produit un tableau contenant des informations/statistiques lexicales de base concernant les TRS en entrée.
