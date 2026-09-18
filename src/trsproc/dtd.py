from functools import lru_cache
from io import StringIO

from lxml import etree

dtd_string = """<?xml encoding="UTF-8"?>

<!ELEMENT Trans ((Speakers|Topics)*,Episode)>
<!ATTLIST Trans
	audio_filename	CDATA		#IMPLIED
	scribe		CDATA		#IMPLIED
	xml:lang	NMTOKEN		#IMPLIED
	version		NMTOKEN		#IMPLIED
	version_date	CDATA		#IMPLIED
	elapsed_time	CDATA		"0"
>

<!ELEMENT Episode (Section*)>
<!ATTLIST Episode
	program		CDATA		#IMPLIED
	air_date	CDATA		#IMPLIED
>

<!ELEMENT Section (Turn*)>
<!ATTLIST Section
	type		(report | nontrans | filler)	#REQUIRED
	topic		IDREF		#IMPLIED
	startTime	CDATA		#REQUIRED
	endTime		CDATA		#REQUIRED
>

<!ELEMENT Turn (#PCDATA|Sync|Background|Comment|Who|Vocal|Event)*>
<!ATTLIST Turn
	speaker		IDREFS		#IMPLIED
	startTime	CDATA		#REQUIRED
	endTime		CDATA		#REQUIRED
	mode		(spontaneous|planned)		#IMPLIED
	fidelity	(high|medium|low)		#IMPLIED
	channel		(telephone|studio)		#IMPLIED
>

<!ELEMENT Sync EMPTY>
<!ATTLIST Sync
	time		CDATA		#REQUIRED
>

<!ELEMENT Background EMPTY>
<!ATTLIST Background
	time		CDATA		#REQUIRED
        type            NMTOKENS	#REQUIRED
        level           NMTOKENS	#IMPLIED
>

<!ELEMENT Who EMPTY>
<!ATTLIST Who
	nb		NMTOKEN         #REQUIRED
>

<!-- **** Speech/non speech events, comments **** -->

<!ELEMENT Vocal EMPTY>
<!ATTLIST Vocal
	desc		CDATA		#REQUIRED
>

<!ELEMENT Event EMPTY>
<!ATTLIST Event
	type		(noise|lexical|pronounce|language|entities)	"noise"
	extent		(begin|end|previous|next|instantaneous)	"instantaneous"
	desc		CDATA		#REQUIRED
>

<!ELEMENT Comment EMPTY>
<!ATTLIST Comment
	desc		CDATA		#REQUIRED
>

<!-- ********** List of Speakers ************** -->

<!ELEMENT Speakers (Speaker*)>
<!ATTLIST Speakers>

<!ELEMENT Speaker EMPTY>
<!ATTLIST Speaker
	id		ID		#REQUIRED
	name		CDATA		#REQUIRED
	check		(yes|no)	#IMPLIED
	type 		(male|female|child|unknown)	#IMPLIED
	dialect		(native|nonnative)		#IMPLIED
	accent		CDATA		#IMPLIED
	scope		(local|global)	#IMPLIED
>

<!-- ********** List of Topics ************** -->

<!ELEMENT Topics (Topic*)>
<!ATTLIST Topics>

<!ELEMENT Topic EMPTY>
<!ATTLIST Topic
	id		ID		#REQUIRED
	desc		CDATA		#REQUIRED
>
"""

lenient_dtd_string = """<?xml encoding="UTF-8"?>

<!ELEMENT Trans ((Speakers|Topics)*,Episode)>
<!ATTLIST Trans
	audio_filename	CDATA		#IMPLIED
	scribe		CDATA		#IMPLIED
	xml:lang	NMTOKEN		#IMPLIED
	version		NMTOKEN		#IMPLIED
	version_date	CDATA		#IMPLIED
	elapsed_time	CDATA		"0"
>

<!ELEMENT Episode (Section*)>
<!ATTLIST Episode
	program		CDATA		#IMPLIED
	air_date	CDATA		#IMPLIED
>

<!ELEMENT Section (Turn*)>
<!ATTLIST Section
	type		CDATA	#REQUIRED
	topic		IDREF		#IMPLIED
	startTime	CDATA		#REQUIRED
	endTime		CDATA		#REQUIRED
>

<!ELEMENT Turn (#PCDATA|Sync|Background|Comment|Who|Vocal|Event)*>
<!ATTLIST Turn
	speaker		IDREFS		#IMPLIED
	startTime	CDATA		#REQUIRED
	endTime		CDATA		#REQUIRED
	mode		CDATA		#IMPLIED
	fidelity	CDATA		#IMPLIED
	channel		CDATA		#IMPLIED
>

<!ELEMENT Sync EMPTY>
<!ATTLIST Sync
	time		CDATA		#REQUIRED
>

<!ELEMENT Background EMPTY>
<!ATTLIST Background
	time		CDATA		#REQUIRED
        type            NMTOKENS	#REQUIRED
        level           NMTOKENS	#IMPLIED
>

<!ELEMENT Who EMPTY>
<!ATTLIST Who
	nb		NMTOKEN         #REQUIRED
>

<!-- **** Speech/non speech events, comments **** -->

<!ELEMENT Vocal EMPTY>
<!ATTLIST Vocal
	desc		CDATA		#REQUIRED
>

<!ELEMENT Event EMPTY>
<!ATTLIST Event
	type		CDATA	"noise"
	extent		CDATA	"instantaneous"
	desc		CDATA		#REQUIRED
>

<!ELEMENT Comment EMPTY>
<!ATTLIST Comment
	desc		CDATA		#REQUIRED
>

<!-- ********** List of Speakers ************** -->

<!ELEMENT Speakers (Speaker*)>
<!ATTLIST Speakers>

<!ELEMENT Speaker EMPTY>
<!ATTLIST Speaker
	id		ID		#REQUIRED
	name		CDATA		#REQUIRED
	check		CDATA	#IMPLIED
	type 		CDATA	#IMPLIED
	dialect		CDATA		#IMPLIED
	accent		CDATA		#IMPLIED
	scope		CDATA	#IMPLIED
>

<!-- ********** List of Topics ************** -->

<!ELEMENT Topics (Topic*)>
<!ATTLIST Topics>

<!ELEMENT Topic EMPTY>
<!ATTLIST Topic
	id		ID		#REQUIRED
	desc		CDATA		#REQUIRED
>
"""


@lru_cache
def _load_dtd() -> etree.DTD:
    f = StringIO(dtd_string)
    return etree.DTD(f)


@lru_cache
def _load_lenient_dtd() -> etree.DTD:
    """This is a more lenient version of the dtd, that only cares about the order of the elements.
    All closed value sets for attribs are turned into plain CDATA,
    because optional invalid attribs fallback to None
    (see [`TrsprocModel._drop_invalid_if_optional`]
    [trsproc.models.TrsprocModel._drop_invalid_if_optional])
    """
    f = StringIO(lenient_dtd_string)
    return etree.DTD(f)
