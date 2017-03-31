# This Python file uses the following encoding: utf-8

import sys
import os
import pretty_midi
from encoder_decoder_lib import NEW_TICK, REST, DEFAULT_RESOLUTION

def ticksToNotes(ticks, tickrate):
    notes = []
    noteDict = {}
    time = 0
    lastPitchNums = []
    for tick in ticks:
        if tick == REST:
            time += tickrate
            continue
        pitches = list(tick)
        pitchNums = []
        for pitch in pitches:
            pitchNum = ord(pitch)
            pitchNums.append(ord(pitch))
            if (pitchNum in lastPitchNums):
                lastPitchNums.remove(pitchNum)
            else:
                note = pretty_midi.Note(velocity = 100, pitch = pitchNum, start = time, end = time)
                noteDict[pitchNum] = note
        if (len(lastPitchNums) > 0):
            for pitchNum in lastPitchNums:
                note = noteDict[pitchNum]
                note.end = time
                notes.append(note)
                noteDict.pop(pitchNum, None)
        lastPitchNums = pitchNums
        time += tickrate 
    return notes

def decodeTextToMidi(filepath, writepath):
    filepath = os.path.abspath(filepath)
    writepath = os.path.abspath(writepath)
    with open(filepath, 'r') as f:
        songText = f.read()
    ticks = songText.split(NEW_TICK)
    notes = ticksToNotes(ticks, 0.014)
    
    midi = pretty_midi.PrettyMIDI()
    piano_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
    piano = pretty_midi.Instrument(program = piano_program)
    for note in notes:
        piano.notes.append(note)
    midi.instruments.append(piano)
    midi.write(writepath)
