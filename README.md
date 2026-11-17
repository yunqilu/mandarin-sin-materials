# Mandarin speech-in-noise materials (QuickSIN / WIN formats)

Scripts that build two Mandarin speech-in-noise tests from existing recordings:

| Output | Source material | Format follows |
|---|---|---|
| `BKBSIN_Mandarin_SIN/` | Mandarin BKB-SIN (`BKBSIN_Mandarin_C/`) | QuickSIN: one sentence per file |
| `WIN_Mandarin/` | MSP disyllables (Fu et al., 2011; Li et al., 2017) + Mandarin 4-talker babble from the BKB/HOPE corpus | Words-in-Noise (WIN) |

**No audio is stored in this repository.** The source materials are licensed or copyrighted and are kept on the lab drive. The `.gitignore` excludes audio, score sheets and documents.

## Setup

```bash
pip install -r requirements.txt
```

Put this repository inside the data folder, or point `SIN_DATA_DIR` at it:

```bash
export SIN_DATA_DIR=/path/to/data
```

The data folder must contain:

```
BKBSIN_Mandarin_A_Quiet/   # quiet BKB sentences + BKBMandarinList_output.txt (used for checking only)
BKBSIN_Mandarin_B_Quiet/   # HOPE items, stereo (L = speech, R = babble) + .txt transcripts (GBK)
BKBSIN_Mandarin_C/         # Mandarin BKB-SIN tracks (L = speech, R = babble) + scoring sheet .xls
msp_disyllables/           # MSP disyllables + rename_mapping.csv
```

Outputs are written back into the data folder. Intermediate JSON files go to `intermediate/` (ignored by git).

## Pipeline

Run in order:

| Script | What it does |
|---|---|
| `scripts/01_parse_scoresheet.py` | Reads the BKB-SIN scoring sheet (.xls) into JSON. Fixes the mislabeled practice block: the 2nd block on sheet 练1 is labeled 练2A but is practice list 1B. |
| `scripts/02_segment_bkbsin.py` | Finds the 10 sentences in each BKB-SIN track (carrier + sentence) from the speech channel, and matches each sentence against the HOPE recordings (B set) by envelope correlation. |
| `scripts/03_check_transcripts_vs_B.py` | Checks score-sheet text against the B-set transcripts wherever the audio match is strong (r > 0.98). |
| `scripts/04_check_transcripts_vs_A.py` | Same check against the A-set (quiet) recordings. |
| `scripts/05_build_bkbsin_quicksin.py` | Builds `BKBSIN_Mandarin_SIN/`. |
| `scripts/06_build_win_mandarin.py` | Builds `WIN_Mandarin/`. |

## Mandarin BKB-SIN in QuickSIN format

- The speech and babble channels are summed to mono. **SNRs are not changed**; re-joining the 10 segments of a list reproduces the summed original sample for sample.
- Nominal SNR per sentence: +21, +18, ... , −6 dB (3-dB steps). Measured per-sentence SNRs track this within about ±2–3 dB (per-item difficulty adjustment in the original corpus).
- Each file runs from the midpoint of the gap before the carrier word to the midpoint of the gap after the sentence. The first file starts at the beginning of the track and the last runs to its end.
- Mono, 44.1 kHz, 16-bit PCM. Naming: `BKBSIN_Mandarin_List1A/BKBSIN_Mandarin_List1A_Sentence1.wav`.
- Transcripts: one `.txt` per list and `BKBSIN_Mandarin_transcripts.csv`. Punctuation and spaces are removed, keywords are kept in their scoring units, and the digit 9 is written as 九.

## WIN_Mandarin (MSP disyllables)

- 10 lists × 35 words. As in WIN: 7 SNR levels × 5 words, babble at a fixed level, word level varied.
- SNR ladder: **+12, +9, +6, +3, 0, −3, −6 dB** (`LADDER` in `06_build_win_mandarin.py`). MSP has only been validated in quiet, so there is no published SNR for it. The ladder uses the 3-dB step of the Mandarin BKB-SIN and covers the adult and child Mandarin BKB SNR50s (−5.9 and −2.0 dB; Xi et al., 2023).
- SNR definition: RMS of the silence-trimmed word vs. RMS of the babble in the same file.
- Babble: right channel of the B-set items, each normalized, joined with 50-ms crossfades (~10 min), excerpts drawn with a fixed random seed. Babble RMS = −37.1 dBFS, the median measured in the original WIN files.
- Timing from the WIN files (medians): 1.36 s babble before the word, 1.58 s after it, 5-ms fades at the file edges.
- MSP recordings are resampled from 22.05 to 44.1 kHz. Output: mono, 44.1 kHz, 16-bit PCM.
- Naming: `WIN_Mandarin_List1/WIN_Mandarin_L1_Word1_cha2ye4.wav`.
- Scoring (Spearman–Kärber, as in WIN): $\text{SNR}_{50} = 12 + \tfrac{3}{2} - 3\cdot\tfrac{\text{words correct}}{5} = 13.5 - 0.6\times\text{words correct}$.
- `WIN_Mandarin_transcripts.csv` lists hanzi, pinyin (neutral tone written as 5) and SNR, and flags the 8 lists Li et al. (2017) found equivalent for CI users (all except Lists 2 and 3). The column is named `Fu2017_equivalent_list` because the lab literature review cites this paper as "Fu 2017" (Fu is the senior author).

## Known issues

- BKB-SIN lists 1B, 2B, 8A and 8B are on the scoring sheet but have no audio.
- Practice list 1B, sentence 2 is distorted in the original recording (both channels clip around 10.0–10.7 s); the summed output is clipped there.
- Score-sheet text for BKB-SIN lists 6B and 7B could not be checked against audio (no matching recordings in the A or B sets).
- `msp_disyllables/rename_mapping.csv` writes neutral tones as 5; 20 of the source file names use citation tones instead. Outputs follow the mapping.

## References

- Fu, Q.-J., Zhu, M., & Wang, X. (2011). Development and validation of the Mandarin speech perception test. *JASA Express Letters*, 129(6), EL267–EL273. doi:10.1121/1.3590739
- Li, Y., Wang, S., Su, Q., Galvin, J. J., & Fu, Q.-J. (2017). Validation of list equivalency for Mandarin speech materials to use with cochlear implant listeners. *Int J Audiol*, 56(sup2), S31–S40.
- Xi, X., et al. (2023). List equivalency and critical differences of a Mandarin Bamford-Kowal-Bench sentence in babble noise test for adults and preschool children with normal hearing. *JSLHR*, 66(12), 5061–5070.
