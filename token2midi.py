import mido
from mido import Message, MidiFile, MidiTrack
import sys

class Parser:
	NOTE_MAP = {
		'C': 24,
		'C#': 25,
		'Db': 25, # 'Db' is equivalent to 'C#
		'D': 26,
		'D#': 27,
		'Eb': 27, # 'Eb' is equivalent to 'D#
		'E': 28,
		'F': 29,
		'F#': 30,
		'Gb': 30, # 'Gb' is equivalent to 'F#
		'G': 31,
		'G#': 32,
		'Ab': 32, # 'Ab' is equivalent to 'G#
		'A': 33,
		'A#': 34,
		'Bb': 34, # 'Bb' is equivalent to 'A#
		'B': 35
	}
	DRUM_MAP = {
		'BD': 36,
		'KD': 36,
		'SD': 38,
		'SN': 38,
		'HH': 42,
		'CHH': 42,
		'CH': 42,
		'CY': 49,
		'RD': 51,
		'HT': 48,
		'LT': 47,
		'Timpani': 41,
	}
	tempo = 120
	tracks = {
		'drums': {
			'notes': []
		},
	}
	currentTrack = None
	barResolution = 64
	currentBar = 0

	def parse(self, notation):
		for line in notation.split('\n'):
			line = line.strip()

			if line.startswith('TEMPO'):
				self.tempo = self._getVal(line)
			elif line.startswith('BAR_RESOLUTION'):
				self.barResolution = self._getVal(line)
			elif line.startswith('INSTRUMENT'):
				parts = line.split()

				instrument = self._getVal(parts[0])
				program = self._getVal(parts[1])

				# create track
				self.tracks[instrument] = {
					'instrument': instrument,
					'program': program,
					'notes': []
				}
				self.currentTrack = instrument
			elif line.startswith('BAR_START'):
				self.currentBar += 1
			elif line.startswith('DRUMS'):
				self.currentTrack = 'drums'
			elif line.startswith('TRACK='):
				self.currentTrack = self._getVal(line)
			elif line.startswith('NOTE'):
				parts = line.split()

				note = self._getVal(parts[0])
				start = self._getVal(parts[1])
				duration = self._getVal(parts[2])

				self._addNoteToTrack(note, start, duration)

		self._sortNotes()

	def save(self, filename):
		# Create a new MIDI file and track
		midi = MidiFile(ticks_per_beat=int(self.barResolution/4))

		for name, track in self.tracks.items():
			if name == 'drums':
				channel = 9
				program = 0
			else:
				channel = 0
				program = track['program']

			print('Creating track: ' + name)

			midi.tracks.append(self._createMidiTrack(track, channel, program))

		midi.save(filename)

	def _getVal(self, term):
		value = term.split('=')[1]
		# if it's an int cast it to int
		if value.isdigit():
			return int(value)

		return value

	def _parseNote(self, note):
		# Extract the pitch and octave from the note string
		if note in self.DRUM_MAP:
			return self.DRUM_MAP[note]
		elif len(note) == 2:
			pitch, octave = note[0], int(note[1])
		elif len(note) == 3:
			pitch, octave = note[:2], int(note[2])
		else:
			return

		# Return the MIDI note number
		if pitch not in self.NOTE_MAP:
			return
		return self.NOTE_MAP[pitch] + (octave) * 12

	def _addNoteToTrack(self, note, start, duration):
		note = self._parseNote(note)
		if not note:
			return
		barStartTime = (self.currentBar - 1) * self.barResolution
		# Add the note to the current track
		self.tracks[self.currentTrack]['notes'].append({
			'message': 'note_on',
			'note': note,
			'time': barStartTime + start,
		})
		# add the note off
		self.tracks[self.currentTrack]['notes'].append({
			'message': 'note_off',
			'note': note,
			'time': barStartTime + start + duration,
		})

	def _sortNotes(self):
		for track in self.tracks:
			self.tracks[track]['notes'].sort(key=lambda x: x['time'])
		return self.tracks

	def _createMidiTrack(self, track, channel=0, program=1):
		midiTrack = MidiTrack()
		midiTrack.insert(0, mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.tempo), time=0))
		midiTrack.insert(0, Message('program_change', channel=channel, program=program, time=0))
		# midiTrack.insert(0, mido.MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=64, time=0))

		for index, note in enumerate(track['notes']):
			# time will be the delta time from the previous note
			if index == 0:
				time = note['time']
			else:
				time = note['time'] - track['notes'][index-1]['time']

			midiTrack.append(Message(note['message'], channel=channel, note=note['note'], velocity=64, time=time))

		return midiTrack

# Arguments
inputFile = sys.argv[1]
outputFile = sys.argv[2]

# Read the tokenized notation from input file
f = open(inputFile, "r")
notation = f.read()
f.close()

# Parse the tokenized notation
parser = Parser()
parser.parse(notation)
parser.save(outputFile)
print('MIDI file saved as ' + outputFile)
