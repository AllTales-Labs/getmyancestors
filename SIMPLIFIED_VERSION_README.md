# Simplified getmyancestors Version

## Overview

This is a simplified version of the getmyancestors script that extracts only essential information from FamilySearch profiles, significantly reducing the amount of data downloaded and processed.

## What Changed

### Data Extraction Simplified

The original script extracted **everything** for each person:

- All names (nicknames, birth names, married names, aliases)
- All facts (birth, death, marriage, occupation, military service, residence, etc.)
- All sources (hundreds per person in many cases)
- All notes and contributor lists
- All memories (photos, documents, stories)
- LDS ordinances
- Family relationships and detailed marriage information

### New Simplified Output

The simplified version now extracts **only**:

1. **Name** - Primary/preferred name only
2. **Birth/death dates and locations** - Essential life events only
3. **Profile ID** - FamilySearch ID for reference
4. **Brief history/bio** - Text-based memories from the "memories" tab
5. **Wikipedia sources only** - Filters out all other sources (when `--get-sources` is used)

## Key Modifications

### 1. Individual Data Extraction (`Indi.add_data()`)

- **Names**: Only extracts the preferred name, skips nicknames, birth names, aliases
- **Facts**: Only extracts birth and death facts, skips all others
- **Sources**: Only includes sources that contain "wikipedia" or "wiki" in URL, title, or citation (when enabled)
- **Memories**: Only extracts text-based memories (bios/histories), ignores photos/documents
- **Life Sketch**: Preserved as it contains important biographical information

### 2. Source Filtering

The script now checks each source for Wikipedia references:

```python
is_wikipedia = False
if "about" in source:
    url = source["about"].lower()
    if "wikipedia" in url or "wiki" in url:
        is_wikipedia = True
if "titles" in source:
    title = source["titles"][0]["value"].lower()
    if "wikipedia" in title or "wiki" in title:
        is_wikipedia = True
if "citations" in source:
    citation = source["citations"][0]["value"].lower()
    if "wikipedia" in citation or "wiki" in citation:
        is_wikipedia = True
```

### 3. Removed Features

- **Contributors**: No longer downloads contributor lists
- **LDS Ordinances**: Removed temple work information
- **Detailed Notes**: Only keeps essential notes, filters out contributor notes
- **Family Sources**: Removed source extraction from family relationships
- **Multiple Names**: Only keeps preferred name
- **All Other Facts**: Only birth/death facts are kept

### 4. Command Line Options

- `--get-sources`: Download Wikipedia sources (adds significant time)
- `--get-notes`: Download individual notes (adds significant time)
- `-c, --get_ordinances`: LDS ordinances option removed
- `-r, --get-contributors`: Contributors option removed

## Usage

### Basic Usage (No Sources)

```bash
python -m getmyancestors.getmyancestors -u username -p password -i PERSON_ID -o output.ged
```

### With Wikipedia Sources

```bash
python -m getmyancestors.getmyancestors -u username -p password -i PERSON_ID --get-sources -o output.ged
```

### With Sources and Notes

```bash
python -m getmyancestors.getmyancestors -u username -p password -i PERSON_ID --get-sources --get-notes -o output.ged
```

### Examples

Download 4 generations of ancestors for a specific person:

```bash
python -m getmyancestors.getmyancestors -u your_username -p your_password -i LF7T-Y4C -o simplified_output.ged -v
```

Download 6 generations with Wikipedia sources:

```bash
python -m getmyancestors.getmyancestors -a 6 --get-sources -u username -p password -i LF7T-Y4C -o output.ged
```

## Benefits

1. **Much Faster**: Significantly reduced API calls and data processing
2. **Smaller Files**: GEDCOM files will be much smaller
3. **Focused Data**: Only the most important information is extracted
4. **Wikipedia Sources**: Only high-quality, verified sources are included (when enabled)
5. **Cleaner Output**: No clutter from duplicate records or low-quality sources

## Expected Output

The simplified GEDCOM will contain:

- Individual records with name, gender, birth/death facts only
- Family relationships (parents, spouses, children)
- Wikipedia sources (only when `--get-sources` is used)
- Brief biographical notes from memories (only when `--get-notes` is used)
- Profile IDs for reference

## Testing

Run the test script to verify the simplified version works:

```bash
python3 test_simplified.py
```

This will test:

- Import functionality
- Simplified Indi class
- Wikipedia source filtering logic

## File Size Comparison

**Before**: A typical 4-generation download could produce a 50-100MB GEDCOM file with thousands of sources
**After**: The same download should produce a 1-5MB GEDCOM file with only Wikipedia sources (when enabled)

## Notes

- The script maintains the same authentication and API structure
- All family relationships are preserved
- The GEDCOM format is still standard-compliant
- You can still use the merge functionality with other GEDCOM files
- The GUI version (`fstogedcom`) will also use the simplified extraction
- Sources are only downloaded when `--get-sources` flag is used
- Notes are only downloaded when `--get-notes` flag is used

## Reverting to Original

If you need the full version again, you can restore the original files from your git repository or reinstall the original package.
