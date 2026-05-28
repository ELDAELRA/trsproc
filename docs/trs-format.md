# TRS Format Specification

> TRS is the XML format used by [Transcriber](https://sourceforge.net/projects/trans/) speech annotation tools for storing transcription, speaker information, named entity annotations, and language tags. The `trsproc` module is built around this format.

---

## 1. Overview

TRS is an XML-based speech transcription format originally defined by the Transcriber software. Its core capabilities are:

- **Segmentation**: Split long recordings into meaningful segments by time
- **Transcription**: Add text transcriptions for each speech segment
- **Annotation**: Mark speaker turns, named entities, language switches, acoustic events, etc.

TRS files are typically paired with corresponding audio files (e.g., `.wav`), linked by filename (e.g., `en_test.trs` corresponds to `en_test.wav`).

---

## 2. XML Declaration & DTD

Every TRS file begins with the following declaration:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Trans SYSTEM "trans-14.dtd">
```

- **Encoding**: Always `UTF-8`
- **DTD**: References `trans-14.dtd`, which defines the document type for the TRS format. The DTD files are included in this project at `docs/transcriber/trans-14.dtd` (standard) and `docs/transcriber/trans-cha.dtd` (CHILDES variant, see [Section 10](#10-dtd-variants-trans-14dtd-vs-trans-chadtd))

---

## 3. Element Hierarchy

```
Trans                          (root element)
├── Topics?                    (topic list container, optional)
│   └── Topic*                (topic definition, repeatable)
├── Speakers?                 (speaker list container, optional)
│   └── Speaker*              (speaker definition, repeatable)
└── Episode                   (episode/recording, unique)
    └── Section+              (section, repeatable)
        └── Turn+             (speech turn, repeatable)
            ├── Sync+         (synchronization point)
            ├── Background*   (background sound annotation)
            ├── Event*        (event annotation)
            ├── Vocal*        (vocal sound annotation)
            ├── Comment*      (comment annotation)
            ├── Who*          (multi-speaker identification)
            └── (text content)(transcription text, as mixed content)
```

> **Note**: `?` means optional (zero or one), `*` means repeatable (zero or more), `+` means at least one occurrence. `Turn` uses a **mixed content model**, where XML child elements and plain text can be interleaved. The `Speakers` and `Topics` containers may appear in any order before `Episode`.

---

## 4. Element Reference

### 4.1 `<Trans>` — Root Element

The root element of a TRS file, containing all transcription information.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `scribe` | No | Name of the tool/person that created or processed the file. Examples: `"trsproc_test"`, `"tgrs"`, empty string for VAD-generated files |
| `audio_filename` | No | Corresponding audio filename (**without extension**). Example: `"en_test"` |
| `version` | No | TRS format version number. Fixed at `"4"` in this project |
| `version_date` | No | Version date, typically an empty string `""` |
| `xml:lang` | No | Default language of the transcription (ISO 639 code). Example: `"en"`, `"fr"` |
| `elapsed_time` | No | Elapsed processing time. Defaults to `"0"` |

Example:

```xml
<Trans scribe="trsproc_test" audio_filename="en_test" version="4" version_date="">
```

---

### 4.2 `<Speakers>` / `<Speaker>` — Speaker Definitions

`<Speakers>` is a container element for the speaker list. It has no attributes and contains zero or more `<Speaker>` elements.

`<Speaker>` is an empty element (self-closing tag) that defines a speaker:

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Speaker identifier, format: `"spk"` + number. Examples: `"spk1"`, `"spk2"` |
| `name` | Yes | Speaker name/label. Examples: `"fs1"`, `"ms1"`, `"a transcrire"` (French for "to transcribe") |
| `check` | No | Whether verified: `"yes"` or `"no"`. Absent in VAD-generated TRS |
| `type` | No | Speaker type. Known values: `"male"`, `"female"`, `"child"`, `"unknown"`. Absent in VAD-generated TRS |
| `dialect` | No | Speaker dialect: `"native"` or `"nonnative"` |
| `accent` | No | Speaker accent (free text) |
| `scope` | No | Speaker scope: `"local"` or `"global"` |

Example:

```xml
<Speakers>
  <Speaker id="spk1" name="fs1" check="no" type="female"/>
  <Speaker id="spk2" name="ms1" check="no" type="male"/>
</Speakers>
```

Simplified form in VAD mode:

```xml
<Speakers>
  <Speaker id="spk1" name="a transcrire"/>
</Speakers>
```

---

### 4.3 `<Episode>` — Episode

A container for `<Section>` elements. There is exactly one `<Episode>` per TRS file.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `program` | No | Program name the recording belongs to |
| `air_date` | No | Broadcast date |

```xml
<Episode>
  <Section type="report" startTime="0" endTime="120.491">
    ...
  </Section>
</Episode>
```

---

### 4.4 `<Section>` — Section

Defines a logical section within a recording (e.g., a report, a music segment, etc.).

| Attribute | Required | Description |
|-----------|----------|-------------|
| `type` | Yes | Section type: `"report"` (standard transcription), `"nontrans"` (non-transcribable), or `"filler"` (filler content) |
| `topic` | No | Topic ID, referencing a `<Topic>` `id` |
| `startTime` | Yes | Section start time (seconds), typically `"0"` |
| `endTime` | Yes | Section end time (seconds), corresponding to audio duration. Example: `"120.491"` |

Example:

```xml
<Section type="report" startTime="0" endTime="120.491">
```

> **Tip**: The `trsproc tmp` command can extract content from specific sections by `type` (default: `"report"`).

---

### 4.5 `<Turn>` — Speech Turns

Defines a speech turn — the core content-bearing element. `<Turn>` uses a **mixed content model** where XML child elements (`<Sync>`, `<Event>`, `<Who>`) and plain text content can be interleaved.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `speaker` | No | Speaker ID, referencing a `<Speaker>` `id`. **If there is no speaker (e.g., silence), this attribute is omitted**. For multiple speakers, the value is a space-separated ID list (e.g., `"spk1 spk3"`) |
| `startTime` | Yes | Turn start time (seconds) |
| `endTime` | Yes | Turn end time (seconds) |
| `mode` | No | Speech mode: `"spontaneous"` or `"planned"` |
| `fidelity` | No | Recording quality: `"high"`, `"medium"`, or `"low"` |
| `channel` | No | Channel type: `"telephone"` or `"studio"` |

Example (with speaker):

```xml
<Turn speaker="spk1" startTime="0.0" endTime="4.789">
<Sync time="0.0"/>
The town of Lyon is served by the Coahoma County School District.
</Turn>
```

Example (no speaker — silence/noise segment):

```xml
<Turn startTime="20.966" endTime="26.633">
<Sync time="20.966"/>
<Event desc="nontrans" type="noise" extent="instantaneous"/>
</Turn>
```

---

### 4.6 `<Sync>` — Synchronization Points

Marks a time synchronization point as the starting boundary of a segment. Every `<Turn>` must begin with a `<Sync>`.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `time` | Yes | Synchronization time point (seconds), must equal the parent Turn's `startTime` |

Example:

```xml
<Sync time="0.0"/>
```

> **Note**: The parser treats content between each `<Sync>` as an independent **segment**. In multi-speaker Turns, multiple `<Sync>` elements may appear to mark different time points within the same turn.

---

### 4.7 `<Background>` — Background Sound Annotations

Marks background audio content within a Turn. It is an empty element (self-closing tag).

| Attribute | Required | Description |
|-----------|----------|-------------|
| `time` | Yes | Time point when the background sound starts (seconds) |
| `type` | Yes | Background sound type (space-separated tokens, e.g., `"music"`, `"other"`) |
| `level` | No | Background sound level (space-separated tokens) |

Example:

```xml
<Background time="5.2" type="music" level="low"/>
```

---

### 4.8 `<Event>` — Event Annotations

`<Event>` is the most complex inline annotation element in the TRS format. It is an empty element (self-closing tag) used to mark various types of events:

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `desc` | Yes | — | Event description; specific values depend on `type` (see below) |
| `type` | No | `"noise"` | Event type: `"noise"`, `"lexical"`, `"pronounce"`, `"language"`, or `"entities"` |
| `extent` | No | `"instantaneous"` | Event scope: `"instantaneous"`, `"begin"`, `"end"`, `"previous"`, or `"next"` |

#### 4.8.1 `type="noise"` — Noise / Non-Speech Events

Marks non-speech acoustic events.

| `desc` value | `extent` value | Meaning |
|--------------|----------------|---------|
| `"nontrans"` | `"instantaneous"` | Non-transcribable segment (silence, noise, etc.), marking an entire segment with no speech content |
| `"pi"` | any | Pronunciation problem / uncertain |

Example (non-transcribable):

```xml
<Event desc="nontrans" type="noise" extent="instantaneous"/>
```

Example (pronunciation uncertain):

```xml
<Event desc="pi" type="noise" extent="instantaneous"/>
```

> **Note**: `"nontrans"` can also appear as plain text `[nontrans]` in the transcription (see [Special Markers in Text Content](#5-special-markers-in-text-content)). The parser recognizes both forms.

#### 4.8.2 `type="language"` — Language Tags

Marks the language of the transcribed text. `begin` and `end` are used in pairs to wrap content in a specific language.

| `desc` value | `extent` value | Meaning |
|--------------|----------------|---------|
| Language code (e.g., `"fr"`, `"en"`) | `"begin"` | Language tag start |
| Language code | `"end"` | Language tag end |

Example:

```xml
<Event desc="fr" type="language" extent="begin"/>
Après les réparations, l'avion a décollé.
<Event desc="fr" type="language" extent="end"/>
```

> **Tip**: The `trsproc lang` command can automatically add language tags to untagged segments, or modify existing tags using a JSON dictionary.

#### 4.8.3 `type="entities"` — Named Entity Annotations

Marks named entities in the text. `begin` and `end` are used in pairs to wrap entity text.

| `desc` value | `extent` value | Meaning |
|--------------|----------------|---------|
| Entity class (e.g., `"loc"`, `"pers"`, `"org"`) | `"begin"` | Named entity start |
| Entity class | `"end"` | Named entity end |

Example:

```xml
The town of
<Event desc="loc" type="entities" extent="begin"/>
Lyon
<Event desc="loc" type="entities" extent="end"/>
is served by the Coahoma County School District.
```

> **Tip**: The `trsproc ne` command extracts named entities to a table, `pne` pre-annotates TRS using an entity dictionary, and `cne` cleans NE annotations from TRS files.

#### 4.8.4 `type="pronounce"` — Pronunciation Annotations

Marks pronunciation-related events. Uses the same `desc` and `extent` mechanism as other event types.

| `desc` value | `extent` value | Meaning |
|--------------|----------------|---------|
| `"pi"` | `"instantaneous"` | Pronunciation problem / uncertain (equivalent to `type="noise" desc="pi"`) |

Example:

```xml
<Event desc="pi" type="pronounce" extent="instantaneous"/>
```

#### 4.8.5 `type="lexical"` — Lexical Annotations

Marks lexical-level events (e.g., truncated words, mispronunciations). The `desc` value provides the specific lexical annotation.

Example:

```xml
<Event desc="trunc" type="lexical" extent="instantaneous"/>
```

#### 4.8.6 `extent` Values Summary

| `extent` value | Meaning |
|----------------|---------|
| `"instantaneous"` | Point event at the current position (default) |
| `"begin"` | Start of a span annotation (paired with `"end"`) |
| `"end"` | End of a span annotation (paired with `"begin"`) |
| `"previous"` | Event applies to the preceding content |
| `"next"` | Event applies to the following content |

---

### 4.9 `<Vocal>` — Vocal Sound Annotations

Marks non-speech vocal sounds (e.g., laughter, coughing). It is an empty element (self-closing tag).

| Attribute | Required | Description |
|-----------|----------|-------------|
| `desc` | Yes | Vocal sound description. Examples: `"laugh"`, `"cough"`, `"breath"` |

Example:

```xml
<Vocal desc="laugh"/>
```

---

### 4.10 `<Comment>` — Comment Annotations

Adds an inline comment within a Turn. It is an empty element (self-closing tag).

| Attribute | Required | Description |
|-----------|----------|-------------|
| `desc` | Yes | Comment text (free form) |

Example:

```xml
<Comment desc="unclear passage"/>
```

---

### 4.11 `<Who>` — Multi-Speaker Identification

When multiple speakers talk simultaneously within the same Turn, `<Who>` identifies which speaker the following text belongs to. It is an empty element (self-closing tag).

| Attribute | Required | Description |
|-----------|----------|-------------|
| `nb` | No | Speaker index number (corresponding to the space-separated list in the Turn's `speaker` attribute) |

> **Note**: Segments containing `<Who>` tags are marked as multi-speaker segments (`speaker_type = "multi"`) by the parser and classified as non-transcribable. There are no actual `<Who>` samples in the project test data, but the parser supports this tag.

---

### 4.12 `<Topics>` / `<Topic>` — Topic Definitions

`<Topics>` is a container element for the topic list. It has no attributes and contains zero or more `<Topic>` elements. It appears before `<Episode>` alongside `<Speakers>`.

`<Topic>` is an empty element (self-closing tag) that defines a topic, which can be referenced by `<Section>` via its `topic` attribute:

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Topic identifier. Example: `"tp1"`, `"tp2"` |
| `desc` | Yes | Topic description (free text). Example: `"weather report"` |

Example:

```xml
<Topics>
  <Topic id="tp1" desc="weather report"/>
  <Topic id="tp2" desc="interview"/>
</Topics>
```

When used, a `<Section>` references the topic via its `topic` attribute:

```xml
<Section type="report" topic="tp1" startTime="0" endTime="120.491">
```

---

## 5. Special Markers in Text Content

Within the mixed text content of `<Turn>`, besides events marked via `<Event>`, the following special inline markers are used:

| Marker | Meaning | Example |
|--------|---------|---------|
| `[nontrans]` | Non-transcribable (silence/noise segment). Can appear as plain text or via `<Event desc="nontrans">` | `[nontrans]` |
| `[pronpi]` | Pronunciation problem / uncertain. The parser automatically converts `<Event desc="pi">` to this marker | `Brown was born in Maquoketa, [pronpi].` |
| `(xx)` | Uncertain text by the speaker; the parenthesized portion is uncertain | `(de)stroyed` — the "de" portion of "destroyed" is uncertain |
| `%uh` | Filler/hesitation marker, embedded as plain text in the transcription | `Barleti wrote %uh this work` |
| `[placeholder N]` | Internal placeholder marker used by `trsproc`, where N is a zero-based incrementing index. Used only in the `txt`/`trs` round-trip workflow — **not a standard TRS element** | `[placeholder 0]`, `[placeholder 21]` |

---

## 6. TRS File Variants

Depending on annotation content and origin, TRS files come in several variants.

### 6.1 Basic Transcription File

The most common input format: only `<Sync>` and plain text, no `<Event>` tags.

```xml
<Turn speaker="spk1" startTime="0.0" endTime="4.789">
<Sync time="0.0"/>
The town of Lyon is served by the Coahoma County School District.
</Turn>
```

### 6.2 File with Named Entity Annotations

Embeds `<Event type="entities">` tag pairs within the text:

```xml
<Turn speaker="spk1" startTime="0.0" endTime="4.789">
<Sync time="0.0"/>
The town of
<Event desc="loc" type="entities" extent="begin"/>
Lyon
<Event desc="loc" type="entities" extent="end"/>
is served by the Coahoma County School District.
</Turn>
```

### 6.3 File with Language Tags

Embeds `<Event type="language">` tag pairs within the text:

```xml
<Turn speaker="spk1" startTime="0.0" endTime="4.789">
<Sync time="0.0"/>
<Event desc="fr" type="language" extent="begin"/>
The town of Lyon is served by the Coahoma County School District.
<Event desc="fr" type="language" extent="end"/>
</Turn>
```

### 6.4 Placeholder File

Plain text is replaced with `[placeholder N]`, used for editing and rewriting. Generated by the `trsproc txt` command.

```xml
<Turn speaker="spk1" startTime="0.0" endTime="4.789">
<Sync time="0.0"/>
[placeholder 0]
</Turn>
```

> **Usage**: First use the `txt` command to extract text and a placeholder TRS, edit the text, then use the `trs` command to merge the text back into the TRS structure.

### 6.5 TRS Generated from TextGrid

Generated by the `trsproc tgrs` command from a Praat TextGrid file. Characteristics:

- `scribe` value is the TextGrid's parent directory name
- Empty transcription segments automatically get `<Event desc="nontrans" type="noise" extent="instantaneous"/>`

```xml
<Trans scribe="tgrs" audio_filename="en_test" version="4" version_date="">
```

### 6.6 TRS Generated from VAD

Generated by the `trsproc vad` command from a VAD (Voice Activity Detection) TextGrid file. Characteristics:

- `scribe` is an empty string
- Only one Speaker with `name="a transcrire"` (French for "to transcribe")
- Speaker element lacks `check` and `type` attributes
- Non-speech segments are marked with `<Event desc="nontrans" type="noise" extent="instantaneous"/>`

```xml
<Trans scribe="" audio_filename="en_test" version="4" version_date="">
<Speakers>
<Speaker id="spk1" name="a transcrire"/>
</Speakers>
```

---

## 7. Complete Example

Below is a complete TRS file containing all major elements:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Trans SYSTEM "trans-14.dtd">
<Trans scribe="trsproc_test" audio_filename="en_test" version="4" version_date="">
<Speakers>
<Speaker id="spk1" name="fs1" check="no" type="female"/>
<Speaker id="spk2" name="ms1" check="no" type="male"/>
</Speakers>
<Episode>
<Section type="report" startTime="0" endTime="120.491">

<!-- Basic transcription segment -->
<Turn speaker="spk1" startTime="0.0" endTime="4.789">
<Sync time="0.0"/>
The town of Lyon is served by the Coahoma County School District.
</Turn>

<!-- Segment with named entity annotation -->
<Turn speaker="spk1" startTime="4.789" endTime="9.563">
<Sync time="4.789"/>
The town of
<Event desc="loc" type="entities" extent="begin"/>
Lyon
<Event desc="loc" type="entities" extent="end"/>
is served by the Coahoma County School District.
</Turn>

<!-- Segment with language tag -->
<Turn speaker="spk1" startTime="9.563" endTime="16.031">
<Sync time="9.563"/>
<Event desc="fr" type="language" extent="begin"/>
Après les réparations, l'avion a décollé.
<Event desc="fr" type="language" extent="end"/>
</Turn>

<!-- Non-transcribable segment (no speaker attribute) -->
<Turn startTime="20.966" endTime="26.633">
<Sync time="20.966"/>
<Event desc="nontrans" type="noise" extent="instantaneous"/>
</Turn>

<!-- Segment with pronunciation uncertainty marker -->
<Turn speaker="spk2" startTime="37.066" endTime="41.081">
<Sync time="37.066"/>
Brown was born in Maquoketa, [pronpi].
</Turn>

<!-- Segment with uncertain text -->
<Turn speaker="spk2" startTime="41.081" endTime="46.092">
<Sync time="41.081"/>
This emplacement and a similar tower nearby were (de)stroyed during the Peninsular War.
</Turn>

<!-- Segment with filler word -->
<Turn speaker="spk2" startTime="68.904" endTime="72.271">
<Sync time="68.904"/>
Barleti wrote %uh this work as an eyewitness.
</Turn>

<!-- Segment with plain-text nontrans marker -->
<Turn speaker="spk1" startTime="51.691" endTime="57.827">
<Sync time="51.691"/>
It was named for the small town of Aitape, Sandaun Province, Papua New Guinea. [nontrans]
</Turn>

</Section>
</Episode>
</Trans>
```

---

## 8. Annotator's Guide

### 8.1 Entry Rules

- **Time values**: Use seconds, either integer (e.g., `0`) or decimal (e.g., `88.80396875`)
- **Speaker references**: The `<Turn>` `speaker` attribute must reference a `<Speaker>` `id`
- **Sync consistency**: The first `<Sync>` inside each `<Turn>` must have a `time` value equal to the Turn's `startTime`
- **Event pairing**: `extent="begin"` and `extent="end"` must appear in pairs with matching `desc` values
- **Text format**: Transcription text is written directly inside `<Turn>`, no additional wrapping tags needed

### 8.2 Common Operations

| Operation | Method |
|-----------|--------|
| Mark silence/noise | Create a Turn without `speaker`, containing `<Event desc="nontrans" type="noise" extent="instantaneous"/>`, or simply write `[nontrans]` |
| Mark pronunciation uncertainty | Use `[pronpi]` in the text |
| Mark uncertain text | Wrap the uncertain portion in parentheses, e.g., `(de)stroyed` |
| Mark filler words | Write `%uh`, `%um`, etc. directly in the text |
| Mark named entities | Wrap entity text with `<Event type="entities">` begin/end pair |
| Mark language switch | Wrap foreign-language text with `<Event type="language">` begin/end pair |
| Add a new speaker | Add a new `<Speaker>` element inside `<Speakers>` |

### 8.3 Important Notes

- **Do not delete `<Sync>` elements**: They serve as time anchors for segments; removing them prevents the parser from segmenting correctly
- **Ensure spacing around `<Event>` tags**: Text before and after NE annotations needs appropriate whitespace, otherwise words may become concatenated after merging
- **`[nontrans]` dual representation**: Can be annotated via `<Event>` tag or as plain text. Both forms are recognized by the parser, but the `<Event>` tag form is recommended for consistency
- **Speaker ID naming convention**: Use the incremental format `"spk1"`, `"spk2"`, etc., and avoid duplicate IDs

---

## 9. Developer Reference

### 9.1 Parser Behavior Notes

The `TRSParser` class (in `src/trsproc/parser.py`) uses a **line-by-line scanning** approach to parse TRS files rather than pure DOM parsing, due to the Turn's mixed content model.

| Aspect | Behavior |
|--------|----------|
| Duplicate Speaker IDs | Test samples contain multiple `<Speaker>` elements with the same `id`; the parser uses the last occurrence (dictionary overwrite) |
| Turns without speaker | When a Turn lacks a `speaker` attribute, the parser sets `speaker` to `"NA"` |
| Segment boundaries | The parser treats content between each `<Sync>` as an independent segment |
| `[nontrans]` dual representation | Can appear as `<Event desc="nontrans">` or as plain text `[nontrans]` |
| Multi-speaker segments | Segments containing `<Who>` tags are marked as `speaker_type = "multi"` and classified as non-transcribable; their duration counts toward `dur_nontrans` |
| Language tag nesting | Segments wrapped by language tags are recorded in `lang_dict` for tracking "other language" segment durations |
| Named entity extraction | When `<Event type="entities" extent="begin">` is encountered, the parser records the entity class, start time, segment ID, and entity text (taken from the next line) |
| Token counting | With `lang="eu"`, counts words by space splitting (apostrophes add +1); with `lang="jkz"`, counts UNICODE characters |

### 9.2 TRSParser `contents` Dictionary Structure

Parsed information is stored in the `TRSParser.contents` dictionary:

```
contents[n]              # Segment n (1-indexed)
  ['xmin']               # Segment start time (seconds)
  ['xmax']               # Segment end time (seconds)
  ['duration']           # Segment duration (seconds)
  ['tokens']             # Token count
  ['content']            # Segment transcription text
  ['speaker']            # Speaker ID ("NA" if none)
  ['speaker_type']       # "single" or "multi"
  ['langs']              # Language tag list
  ['SNR']                # Signal-to-noise ratio ("NA" if computation fails)

contents['NE'][n]        # Named Entity n
  ['class']              # Entity class (e.g., "loc", "pers", "org")
  ['xmin']               # Entity start time
  ['segmentID']          # ID of the containing segment
  ['content']            # Entity text

contents[0]              # Overall statistics
  ['totalSegments']      # Total segments
  ['totalWords']         # Total word count
  ['totalNE']            # Total named entities
  ['totalNonTrans']      # Total non-transcribable segments
  ['totalPronPi']        # Total pronunciation uncertainty marks
  ['totalTrans']         # Total transcribed segments
  ['totalLang']          # Total language tags
  ['otherLang']          # Set of other languages used
  ['duration']           # Total duration
  ['durationTrans']      # Transcribed duration
  ['durationNonTrans']   # Non-transcribed duration
  ['meanSNR']            # Mean SNR
```

### 9.3 Edge Cases

| Situation | Handling |
|-----------|----------|
| Missing audio file | `file_duration` is set to `"audio not found"`, SNR computation returns `"NA"` |
| Missing Section tags | `section_duration` is set to `"Section not found"` |
| XML parsing errors | Warning message printed; results may be incorrect |
| Empty transcription segment | Matched by regex `^\[.*\]$` for pure marker content, classified as non-transcribable |

---

## 10. DTD Variants: `trans-14.dtd` vs `trans-cha.dtd`

The project includes two DTD files in `docs/transcriber/`:

| File | Purpose |
|------|---------|
| `trans-14.dtd` | Standard Transcriber 1.4 DTD — the default for most TRS files |
| `trans-cha.dtd` | CHILDES adaptation — extends the standard DTD for child language research |

### 10.1 `trans-cha.dtd` Additional `<Trans>` Attributes

| Attribute | Type | Values | Description |
|-----------|------|--------|-------------|
| `coder` | CDATA | — | Coder identification (for `@coders` in CHILDES) |
| `coding` | CDATA | — | Coding scheme (for `@coding` in CHILDES) |
| `transtype` | Enum | `"hub5"`, `"childes"` | Transcription type |
| `terminatorfile` | CDATA | — | Filename containing CHILDES utterance terminators |
| `filename` | CDATA | — | Source filename |
| `font` | CDATA | — | Font specification |
| `warning` | CDATA | — | Warning message |

### 10.2 `trans-cha.dtd` Additional `<Speaker>` Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `role` | CDATA | Speaker role (e.g., `"Target_Child"`, `"Mother"`) |
| `age` | CDATA | Speaker age (CHILDES age format, e.g., `"3;06.15"`) |
| `birth` | CDATA | Speaker birth date |
| `education` | CDATA | Education level |
| `group` | CDATA | Social group |
| `language` | CDATA | Language spoken |
| `ses` | CDATA | Socioeconomic status |
| `sex` | CDATA | Sex (alternative to `type`) |

### 10.3 `trans-cha.dtd` Additional `<Event>` Types

The `type` attribute supports three additional values:

| `type` value | Description |
|--------------|-------------|
| `"header"` | Header information markers |
| `"dependent"` | Dependent tier annotations |
| `"scope"` | Scope annotations |

### 10.4 Compatibility Notes

- The `trans-cha.dtd` is a **superset** of `trans-14.dtd` — all standard TRS files are valid against either DTD
- Standard TRS files use `<!DOCTYPE Trans SYSTEM "trans-14.dtd">`
- CHILDES-format TRS files use `<!DOCTYPE Trans SYSTEM "trans-cha.dtd">`
- The `trsproc` parser does not validate against a DTD; it handles both variants transparently
