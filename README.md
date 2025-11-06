# MIDI Chord Suggester (Modal)

A live MIDI helper that listens to chords you play and:
- names the chord (including extensions like m9, maj7♯11, etc.),
- shows the scale degree within the chosen mode,
- suggests 2–3 musically sensible next chords (pop / jazz / classical flavors).

It uses:
- **MIDI input** via `mido` (with `python-rtmidi` backend),
- **MIDI thru/output** via `pygame.midi` (so you can route notes to a synth or DAW),
- optional virtual MIDI ports (loopMIDI on Windows, IAC on macOS, ALSA virmidi on Linux).

---

## Features

- Supports major (Ionian, Lydian, Mixolydian) and minor modes (Dorian, Phrygian, Aeolian [natural/harmonic/melodic], Locrian).
- Handles triads, sevenths, and common extensions (maj9, m11, 13, altered doms like 7♭9 / 7♯9, etc.).
- Offers next-chord suggestions using modal cadences, progression rules, and (for jazz) tasteful secondary dominants.

---

## Quick Start

### Prerequisites
- **Python 3.10+** recommended
- System MIDI drivers working (you can test in your DAW or with a virtual port)
- A keyboard/controller or a DAW that can send MIDI into a virtual input

### Install

```bash
# From the repo root
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### Virtual MIDI setup (choose your OS)

**Windows (loopMIDI)**  
1. Install and run **loopMIDI**.  
2. Create a new port (e.g., `loopMIDI Port`).  
3. In your DAW/synth, *listen to* that port (for the thru/out notes).  
4. In your keyboard/DAW, *send MIDI* to the input port you’ll select in the script.

> The script also searches for a loopMIDI output port automatically; if not found, it exits with a friendly message.

**macOS (IAC Driver)**  
1. Open **Audio MIDI Setup → Window → Show MIDI Studio**.  
2. Double-click **IAC Driver**, check **Device is online**, add a port (e.g., `IAC Bus 1`).  
3. Route your DAW/synth to listen to that IAC port; send your controller to it as well.

**Linux (ALSA virmidi)**  
- Create a virtual port, e.g.:
  ```bash
  sudo modprobe snd-virmidi
  aconnect -o    # list outputs
  aconnect -i    # list inputs
  ```
- Connect your controller → virmidi input, and virmidi output → synth/DAW.

> Tip: If `mido` can't find a backend, ensure `python-rtmidi` installed and set:
> `export MIDO_BACKEND=mido.backends.rtmidi` (macOS/Linux) or set an env var on Windows.

---

## Run

```bash
python chord_suggester.py
```

Then follow the prompts:
1. Select a MIDI **input** port from the numbered list.  
2. Enter a tonic (e.g., `C`, `D#`, `Bb`).  
3. Choose **Major** or **Minor** and pick a mode (and Aeolian flavor if minor).  
4. Choose a style: `pop`, `jazz`, or `classical`.  
5. Play **3+ notes**—you’ll see the chord name and suggested next chords.

Press `Ctrl+C` to stop listening and return to the menu. Type `exit` at the tonic prompt to quit.

---

## Troubleshooting

- **“loopMIDI not found!”**  
  Start loopMIDI (Windows) or use IAC on macOS and re-run.  
- **No input ports listed**  
  Your controller/DAW may not be exposing a port. Create a virtual bus and route into it.  
- **No sound**  
  This script *forwards MIDI notes* to a MIDI output (e.g., loopMIDI/IAC). Make sure a synth/DAW is listening to that output.
- **Backend issues (`mido`)**  
  Ensure `python-rtmidi` is installed. If needed:
  ```
  pip install python-rtmidi
  export MIDO_BACKEND=mido.backends.rtmidi
  ```

---

## License
MIT (see `LICENSE`).

## Credits
Built by Scott’s son, Zachary, 👏—documented for future you.
