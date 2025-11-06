# Chord Progression MIDI Generator
# Author: Zachary Franklin
# Repository and documentation by Scott Franklin
# License: MIT


import random
import mido
import pygame.midi
pygame.midi.init()

# 👇 Replace default with loopMIDI
for i in range(pygame.midi.get_count()):
    interf, name, input_, output_, opened = pygame.midi.get_device_info(i)
    if output_ and b'loopMIDI' in name:
        output_id = i
        break
else:
    print("❌ loopMIDI not found! Is it running?")
    exit()

midi_out = pygame.midi.Output(output_id)


active_notes = set()

root_names = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

mode_intervals = {
    "ionian":     [0, 2, 4, 5, 7, 9, 11],
    "dorian":     [0, 2, 3, 5, 7, 9, 10],
    "phrygian":   [0, 1, 3, 5, 7, 8, 10],
    "lydian":     [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian":    [0, 2, 3, 5, 7, 8, 10],
    "aeolian_h":  [0, 2, 3, 5, 7, 8, 11],  # harmonic minor
    "aeolian_m":  [0, 2, 3, 5, 7, 9, 11],  # melodic minor
    "locrian":    [0, 1, 3, 5, 6, 8, 10]
}

mode_chords = {
    'ionian':     ['maj', 'min', 'min', 'maj', 'maj', 'min', 'dim'],
    'dorian':     ['min', 'min', 'maj', 'maj', 'min', 'dim', 'maj'],
    'phrygian':   ['min', 'maj', 'maj', 'min', 'dim', 'maj', 'min'],
    'lydian':     ['maj', 'maj', 'min', 'dim', 'maj', 'min', 'min'],
    'mixolydian': ['maj', 'min', 'dim', 'maj', 'min', 'min', 'maj'],
    'aeolian':    ['min', 'dim', 'maj', 'min', 'min', 'maj', 'maj'],
    'aeolian_h':  ['min', 'dim', 'aug', 'min', 'maj', 'maj', 'dim'],
    'aeolian_m':  ['min', 'min', 'aug', 'maj', 'maj', 'dim', 'dim'],
    'locrian':    ['dim', 'maj', 'min', 'min', 'maj', 'maj', 'min']
}

degree_names = {
    "ionian":     ["I", "ii", "iii", "IV", "V", "vi", "vii°"],
    "dorian":     ["i", "ii", "♭III", "IV", "v", "vi°", "♭VII"],
    "phrygian":   ["i", "♭II", "♭III", "IV", "v", "♭VI", "♭VII"],
    "lydian":     ["I", "II", "iii", "#iv°", "V", "vi", "vii"],
    "mixolydian": ["I", "ii", "iii°", "IV", "v", "vi", "♭VII"],
    "aeolian":    ["i", "ii°", "♭III", "iv", "v", "♭VI", "♭VII"],
    "aeolian_h":  ["i", "ii°", "♭III+", "iv", "V", "VI", "vii°"],
    "aeolian_m":  ["i", "ii", "♭III+", "IV", "V", "vi°", "vii°"],
    "locrian":    ["i°", "♭II", "♭III", "iv", "♭V", "♭VI", "♭VII"]
}

def note_name(midi_num, prefer_flats=False):
    sharp_names = ['C', 'C#', 'D', 'D#', 'E', 'F',
                   'F#', 'G', 'G#', 'A', 'A#', 'B']
    flat_names = ['C', 'Db', 'D', 'Eb', 'E', 'F',
                  'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    names = flat_names if prefer_flats else sharp_names
    return names[midi_num % 12]

def get_scale_degree_name(root_note, tonic_note, mode):
    interval = (root_note - tonic_note) % 12
    mode_ints = mode_intervals.get(mode.lower())
    labels = degree_names.get(mode.lower())

    if mode_ints and labels:
        for i, val in enumerate(mode_ints):
            if val == interval:
                return labels[i]
    return None

def get_progression_rules(mode):
    rules = {
        'ionian': {
            'I': ['IV', 'V', 'vi'],
            'ii': ['V'],
            'iii': ['vi'],
            'IV': ['I', 'V'],
            'V': ['I'],
            'vi': ['ii', 'IV'],
            'vii°': ['I']
        },
        'dorian': {
            'i': ['IV', 'v', '♭VII'],
            'ii': ['v'],
            '♭III': ['vi°'],
            'IV': ['i', '♭VII'],
            'v': ['♭VII', 'i'],
            'vi°': ['ii'],
            '♭VII': ['i']
        },
        'phrygian': {
            'i': ['♭II', '♭VI', '♭VII'],
            '♭II': ['♭VII'],
            '♭III': ['♭VI'],
            '♭VI': ['♭VII', 'i'],
            '♭VII': ['i']
        },
        'lydian': {
            'I': ['II', 'V', 'vi'],
            'II': ['V'],
            'iii': ['vi'],
            '#iv°': ['V'],
            'V': ['I'],
            'vi': ['II', 'iii']
        },
        'mixolydian': {
            'I': ['IV', 'v', '♭VII'],
            'ii': ['v'],
            'iii°': ['vi'],
            'IV': ['I', 'v'],
            'v': ['I'],
            'vi': ['ii'],
            '♭VII': ['I']
        },
        'aeolian': {
            'i': ['iv', '♭VI', '♭VII'],
            'ii°': ['iv'],
            '♭III': ['♭VI'],
            'iv': ['♭VII', 'i'],
            'v': ['♭VI', 'i'],
            '♭VI': ['♭VII', 'i'],
            '♭VII': ['i']
        },
        'aeolian_h': {
            'i': ['iv', 'V', '♭VI'],
            'ii°': ['V'],
            '♭III+': ['VI'],
            'iv': ['V'],
            'V': ['i'],
            'VI': ['ii°'],
            'vii°': ['i']
        },
        'aeolian_m': {
            'i': ['IV', 'V'],
            'ii': ['V'],
            '♭III+': ['VI'],
            'IV': ['V'],
            'V': ['i'],
            'vi°': ['ii'],
            'vii°': ['i']
        },
        'locrian': {
            'i°': ['♭III', 'iv'],
            '♭II': ['♭V'],
            '♭III': ['♭VI'],
            'iv': ['♭VII'],
            '♭V': ['i°'],
            '♭VI': ['♭VII'],
            '♭VII': ['i°']
        }
    }
    return rules.get(mode.lower(), {})

def get_mode_chord_suggestions(tonic_note, mode, prefer_flats):
    suggestions = []
    intervals = mode_intervals.get(mode.lower())
    labels = degree_names.get(mode.lower())

    if not intervals or not labels:
        return ["(Unknown mode)"]

    for i, semitone in enumerate(intervals):
        root_note = (tonic_note + semitone) % 12
        label = labels[i]
        name = note_name(root_note, prefer_flats)

        if "°" in label:
            chord_type = "diminished"
        elif "+" in label or "aug" in label:
            chord_type = "augmented"
        elif label.islower() or "♭" in label or "#" in label or label.startswith("i"):
            chord_type = "minor"
        else:
            chord_type = "major"

        suggestions.append(f"{name} ({label}) [{chord_type}]")
    return suggestions

def get_chord_name(notes, prefer_flats, tonic_note, mode):
    if len(notes) < 3:
        return None

    sorted_notes = sorted(notes)
    best_match = None

    for try_root in sorted_notes:
        intervals = sorted([(n - try_root) % 12 for n in sorted_notes])
        chord_name = note_name(try_root, prefer_flats)
        degree = get_scale_degree_name(try_root, tonic_note, mode)

        # --- EXTENDED CHORDS ---
        if set(intervals) >= {0, 3, 7, 10, 2}:  # m9
            best_match = f"{chord_name}m9 ({degree})" if degree else f"{chord_name}m9"
        elif set(intervals) >= {0, 3, 7, 10, 5}:  # m11
            best_match = f"{chord_name}m11 ({degree})" if degree else f"{chord_name}m11"
        elif set(intervals) >= {0, 4, 7, 11, 2}:  # maj9
            best_match = f"{chord_name}maj9 ({degree})" if degree else f"{chord_name}maj9"
        elif set(intervals) >= {0, 4, 7, 10, 1}:  # 7♭9
            best_match = f"{chord_name}7♭9 ({degree})" if degree else f"{chord_name}7♭9"
        elif set(intervals) >= {0, 4, 7, 10, 3}:  # 7♯9
            best_match = f"{chord_name}7♯9 ({degree})" if degree else f"{chord_name}7♯9"
        elif set(intervals) >= {0, 4, 7, 11, 6}:  # maj7♯11
            best_match = f"{chord_name}maj7♯11 ({degree})" if degree else f"{chord_name}maj7♯11"
        elif set(intervals) >= {0, 4, 7, 10, 9}:  # 13
            best_match = f"{chord_name}13 ({degree})" if degree else f"{chord_name}13"

        # --- SEVENTH CHORDS ---
        elif intervals == [0, 4, 7, 10]:
            best_match = f"{chord_name}7 ({degree})" if degree else f"{chord_name}7"
        elif intervals == [0, 4, 7, 11]:
            best_match = f"{chord_name}maj7 ({degree})" if degree else f"{chord_name}maj7"
        elif intervals == [0, 3, 7, 10]:
            best_match = f"{chord_name}m7 ({degree})" if degree else f"{chord_name}m7"
        elif intervals == [0, 3, 6, 10]:
            best_match = f"{chord_name}m7♭5 ({degree})" if degree else f"{chord_name}m7♭5"

        # --- TRIADS ---
        elif intervals == [0, 4, 7]:
            best_match = f"{chord_name} ({degree})" if degree else f"{chord_name} major"
        elif intervals == [0, 3, 7]:
            best_match = f"{chord_name} ({degree})" if degree else f"{chord_name} minor"
        elif intervals == [0, 3, 6]:
            best_match = f"{chord_name} ({degree})" if degree else f"{chord_name} diminished"

        if best_match:
            break
 
    return best_match or "Unrecognized chord"

modal_cadences = {
    'dorian': [['i', 'IV'], ['IV', 'v'], ['v', 'i']],
    'phrygian': [['i', '♭II'], ['♭II', '♭VII'], ['♭VII', 'i']],
    'lydian': [['I', 'II'], ['II', 'V'], ['V', 'I']],
    'mixolydian': [['I', '♭VII'], ['♭VII', 'IV'], ['IV', 'I']],
    'aeolian': [['i', 'iv'], ['iv', '♭VII'], ['♭VII', 'i']],
    'aeolian_h': [['i', 'V'], ['V', 'i']],
    'aeolian_m': [['i', 'IV'], ['IV', 'V'], ['V', 'i']],
    'locrian': [['i°', '♭II'], ['♭II', '♭VII'], ['♭VII', 'i°']]
}

def suggest_next_chords(current_chord, tonic, mode, style, prefer_flats):
    tonic_index = root_names.index(tonic)
    scale = [(tonic_index + i) % 12 for i in mode_intervals[mode]]
    note_names = [note_name(n, prefer_flats) for n in scale]

    qualities = mode_chords[mode]
    degree_labels = degree_names[mode]
    chords = []

    for i, root in enumerate(note_names):
        qual = qualities[i]
   
        if style == "jazz":
            suffix = {
                'maj': random.choice(['maj7', 'maj9']),
                'min': random.choice(['m7', 'm9']),
                'dim': random.choice(['m7b5', 'dim7']),
                'aug': 'aug7'  # optional jazzy version if you like
            }.get(qual, '')

            # Optional spicy extensions
            if qual == 'maj' and random.random() < 0.2:
                suffix = random.choice(['maj7♯11', 'maj13'])
            elif qual == 'min' and random.random() < 0.2:
                suffix = 'm11'
            elif qual == 'dim' and random.random() < 0.2:
                suffix = 'dim9'
            elif qual == 'aug' and random.random() < 0.2:
                suffix = 'aug9'  # optional spice for augmented
            if degree_labels[i] in ['V', '♭VII'] and random.random() < 0.5:
                suffix = random.choice(['7♭9', '7♯9', '13', '7♯5♭9'])
   
        else:
            suffix_map = {
                'maj': '',
                'min': 'm',
                'dim': 'dim',
                'aug': 'aug'  # 💅 yes ma'am
            }
            suffix = suffix_map.get(qual, '')


        chords.append(f"{root}{suffix}")

    # Fallback degrees by style
    if style == "pop":
        degrees = [0, 5, 3, 4]
    elif style == "jazz":
        degrees = [1, 4, 0, 2, 5]
    elif style == "classical":
        degrees = [0, 4, 0, 3, 1]
    else:
        degrees = list(range(7))

    # Clean chord root for matching
    cleaned_chord = current_chord.split()[0].replace('maj7', '').replace('maj9', '').replace('m7b5', '').replace('m7', '').replace('m9', '').replace('7', '').replace('dim7', '').replace('dim9', '').replace('m11', '')
    current_root = cleaned_chord

    enharmonic_map = {
        'Bb': 'A#', 'Eb': 'D#', 'Ab': 'G#', 'Db': 'C#',
        'Gb': 'F#', 'Cb': 'B', 'Fb': 'E'
    }
    if current_root in enharmonic_map:
        current_root = enharmonic_map[current_root]

    progression_rules = get_progression_rules(mode)
    cadences = modal_cadences.get(mode, [])
    degree = None
    if current_root in note_names:
        degree_index = note_names.index(current_root)
        degree = degree_labels[degree_index]

    # 💫 Favor modal cadences and add secondary dominants when spicy
    cadence_suggestions = []
    if degree:
        for cadence in cadences:
            from_deg, to_deg = cadence
            if from_deg == degree and to_deg in degree_labels:
                target_idx = degree_labels.index(to_deg)
                cadence_suggestions.append(chords[target_idx])

                # 🔥 Optional secondary dominant
                if style == "jazz" and random.random() < 0.5:
                    # Find the root note of the *target* chord
                    target_root = note_names[target_idx]
                    if target_root in root_names:
                        v7_index = (root_names.index(target_root) + 7) % 12
                        v7_root = note_name(v7_index, prefer_flats)
                        sec_dom_chord = f"{v7_root}7"
                        cadence_suggestions.insert(0, sec_dom_chord)


    # 🌈 Blend cadences and progression rules
    rule_suggestions = []
    if degree and degree in progression_rules:
        rule_degrees = progression_rules[degree]
        rule_suggestions = [chords[degree_labels.index(d)] for d in rule_degrees if d in degree_labels]

    # 🧪 Prioritize cadences, add some rules if needed
    suggestions = cadence_suggestions[:2] + rule_suggestions[:2]
    if not suggestions:
        suggestions = [chords[i] for i in degrees if current_root not in chords[i]]

    # 🌶️ Add secondary dominant for spice
    if random.random() < 0.3:
        sec_dom_map = {1: 4, 4: 0, 5: 2}
        possible_targets = [i for i in sec_dom_map if i < len(chords)]
        if possible_targets:
            target_degree = random.choice(possible_targets)
            target_root = note_names[target_degree]
            if target_root in root_names:
                sec_dom_root_index = (root_names.index(target_root) + 7) % 12
                sec_dom_root = note_name(sec_dom_root_index, prefer_flats)
                sec_dom_chord = f"{sec_dom_root}7"
                suggestions.insert(0, sec_dom_chord)

    # 🌐 Detect if current chord is a secondary dominant
    secondary_dominants = {
        "D": "G", "A": "D", "E": "A", "B": "E", "F#": "B", "C#": "F#", "G#": "C#",
        "Db": "Gb", "Ab": "Db", "Eb": "Ab", "Bb": "Eb", "F": "Bb", "C": "F", "G": "C"
    }

    # Strip suffix to get clean root
    raw_root = current_chord.split()[0]

    # Normalize to match keys in secondary_dominants
    enharmonic_reverse = {
        'A#': 'Bb', 'D#': 'Eb', 'G#': 'Ab', 'C#': 'Db', 'F#': 'Gb', 'B': 'Cb', 'E': 'Fb'
    }
    if raw_root in enharmonic_reverse:
        raw_root = enharmonic_reverse[raw_root]

    is_secondary = False
    tonicized = None

    if "m" not in current_chord.lower() and raw_root in secondary_dominants:
        tonicized = secondary_dominants[raw_root]
        if tonicized != tonic:
            is_secondary = True

    # 🌐 Detect if current chord is a secondary dominant
    secondary_dominants = {
        "D": "G", "A": "D", "E": "A", "B": "E", "F#": "B", "C#": "F#", "G#": "C#",
        "Db": "Gb", "Ab": "Db", "Eb": "Ab", "Bb": "Eb", "F": "Bb", "C": "F", "G": "C"
    }

    # Strip suffix to get clean root
    raw_root = current_chord.split()[0]

    # Normalize raw_root enharmonically to match secondary_dominants keys
    enharmonic_map = {
        'A#': 'Bb', 'D#': 'Eb', 'G#': 'Ab', 'C#': 'Db',
        'F#': 'Gb', 'B': 'Cb', 'E': 'Fb'
    }
    if raw_root in enharmonic_map:
        raw_root = enharmonic_map[raw_root]

    is_secondary = False
    tonicized = None

    if "m" not in current_chord.lower() and raw_root in secondary_dominants:
        tonicized = secondary_dominants[raw_root]
        if tonicized != tonic:
            is_secondary = True

        # 🎯 If it's a secondary dominant, resolve to its minor
    if is_secondary:
        if style == "jazz":
            resolution = f"{tonicized}{random.choice(['m7', 'm9', 'm11'])}"
        else:
            resolution = f"{tonicized}m"

        if resolution not in suggestions:
            #print(f"🔍 Secondary dominant detected: {current_chord} → inserting resolution {resolution}")
            suggestions.insert(0, resolution)


        # Normalize tonicized resolution
        resolution_root = tonicized
        if resolution_root not in root_names:
            enharmonic_reverse = {
                'A#': 'Bb', 'D#': 'Eb', 'G#': 'Ab',
                'C#': 'Db', 'F#': 'Gb', 'B': 'Cb', 'E': 'Fb'
            }
            resolution_root = enharmonic_reverse.get(tonicized, tonicized)

        # Pick resolution quality
        if style == "jazz":
            resolution_suffix = random.choice(["m7", "m9", "m11"])
        else:
            resolution_suffix = "m"

        resolution_chord = f"{resolution_root}{resolution_suffix}"

    # 🎲 Wildcard chaos mode
    if random.random() < 0.2:
        flat_7 = (tonic_index + 10) % 12
        flat_3 = (tonic_index + 3) % 12
        flat_6 = (tonic_index + 8) % 12
        wildcards = [note_name(n, prefer_flats) for n in [flat_7, flat_3, flat_6]]
        suggestions.insert(0, random.choice(wildcards))

    return suggestions[:3] if suggestions else chords[:3]

# --- MIDI PORT SELECTION ---
ports = mido.get_input_names()
print("🎛️ Available MIDI ports:")
for i, name in enumerate(ports):
    print(f"  {i}: {name}")
selected = input("🎚️ Enter the number of the port you want to use: ").strip()

try:
    port_name = ports[int(selected)]
except (IndexError, ValueError):
    print("❌ Invalid selection. Exiting.")
    exit(1)

# --- LOOP FOR NEW SESSIONS ---
while True:
    print("\n🔁 New session — type 'exit' to quit.")

    key_input = input("🎼 Enter tonic (e.g. C, D#, F, Bb): ").strip()
    if key_input.lower() == 'exit':
        print("👋 Bye diva!")
        break

    # ✅ Prefer flats if user typed 'b' or it's a flat key
    flat_keys = ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']
    prefer_flats = any(k.lower() in key_input.lower() for k in flat_keys) or 'b' in key_input.lower()

    # 🎵 Initial tonic cleanup (preserve for display)
    if 'm' in key_input.lower() and not key_input.lower().endswith('maj'):
        tonic = key_input.capitalize().replace('m', '')
    else:
        tonic = key_input.capitalize()

    display_tonic = tonic  # Save for printing

    # ♯♭ Internal enharmonic conversion (for processing only!)
    enharmonic_map = {
        'Bb': 'A#', 'Eb': 'D#', 'Ab': 'G#',
        'Db': 'C#', 'Gb': 'F#', 'Cb': 'B', 'Fb': 'E'
    }
    if tonic in enharmonic_map:
        tonic_internal = enharmonic_map[tonic]
    else:
        tonic_internal = tonic

    tonic_note = root_names.index(tonic_internal)  # This gives a MIDI note number

    # Ask for quality *after* we normalize tonic
    quality = input("🌞 Major or 🌚 Minor? ").strip().lower()
   
    if quality == 'major':
        mode_input = input("🎹 Choose major mode (ionian, lydian, mixolydian): ").strip().lower()
        if mode_input not in ['ionian', 'lydian', 'mixolydian']:
            print("⚠️ Unknown major mode. Defaulting to ionian.")
            mode_input = 'ionian'
    elif quality == 'minor':
        mode_input = input("🎹 Choose minor mode (dorian, phrygian, aeolian, locrian): ").strip().lower()
        if mode_input not in ['dorian', 'phrygian', 'aeolian', 'locrian']:
            print("⚠️ Unknown minor mode. Defaulting to dorian.")
            mode_input = 'dorian'
        elif mode_input == 'aeolian':
            flavor = input("🌶 Choose flavor of aeolian (natural, harmonic, melodic): ").strip().lower()
            if flavor == 'harmonic':
                mode_input = 'aeolian_h'
            elif flavor == 'melodic':
                mode_input = 'aeolian_m'
            else:
                mode_input = 'aeolian'  # natural
    else:
        print("⚠️ Unknown quality. Defaulting to C Ionian.")
        tonic = 'C'
        mode_input = 'ionian'

    style_input = input("🎧 Choose style (pop, jazz, classical): ").strip().lower()

    flat_keys = ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']
    prefer_flats = tonic in flat_keys

    print(f"\n🎼 Mode: {display_tonic} {mode_input.replace('_', ' ').capitalize()}")
    print(f"🎧 Style: {style_input}")
    print("🎹 Listening for chords... (Play 3+ notes!)")

    active_notes = set()
    last_chord = None

    try:
        with mido.open_input(port_name) as inport:
            for msg in inport:
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes.add(msg.note)
                    midi_out.note_on(msg.note, msg.velocity)
                elif msg.type in ('note_off', 'note_on') and msg.velocity == 0:
                    active_notes.discard(msg.note)
                    midi_out.note_off(msg.note, 0)

                if len(active_notes) >= 3:
                    chord = get_chord_name(active_notes, prefer_flats, tonic_note, mode_input)
                    if chord and chord != last_chord:
                        print(f"\n🎶 Chord: {chord}")
                        suggestion = suggest_next_chords(chord, tonic_internal, mode_input, style_input, prefer_flats)
                        print(f"👉 Suggested next chords: {', '.join(suggestion)}\n")
                        last_chord = chord

    except KeyboardInterrupt:
        print("\n⏹️  Stopped listening. Returning to menu...\n")

    finally:
        midi_out.close()
        pygame.midi.quit()
