# This Python file uses the following encoding: utf-8

import sys
import os
import pretty_midi
from encoder_decoder_lib import NEW_TICK, REST, DEFAULT_RESOLUTION, DEFAULT_TRACK

class Interval:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.notes = []
        
    def addNote(self, note):
        self.notes.append(note)
    
    def notesAtTime(self, time):
        notesAtTime = []
        for note in self.notes:
            if (note.start < time and note.end > time):
                notesAtTime.append(note)
        return notesAtTime
    

def groupNotesByInterval(instrument):
    intervals = []
    lastEndTime = 0
    i = 0
    while (i < len(instrument.notes)):
        note = instrument.notes[i]
        if (note.end - note.start <= 0):
            i += 1
            continue
        searchIndex = i
        newTime = False
        newIndex = i
        notes = []
        startTime = note.start
        if (startTime < lastEndTime):
            startTime = lastEndTime
        elif(startTime > lastEndTime):
            intervals.append(Interval(lastEndTime, startTime))
        lastEndTime = note.end
        interval = Interval(startTime, lastEndTime)
        while (searchIndex < len(instrument.notes)):
            note = instrument.notes[searchIndex]
            if (note.end > interval.end):
                newTime = True
                newIndex = searchIndex
                
            if (note.end - note.start <= 0):
                continue
            elif (note.start < interval.end):
                interval.addNote(note)
            else:
                break
            searchIndex += 1
        intervals.append(interval)
        i = newIndex
        if (not newTime):
            i = searchIndex
    return intervals
    
def intervalsToTicks(intervals, tickrate):
    ticks = []
    for interval in intervals:
        total_time = interval.end - interval.start
        time = interval.start
        while (time < interval.end):
            pitches = []
            notes = interval.notesAtTime(time)
            for note in notes:
                pitches.append(note.pitch)
            ticks.append(pitches)
            time += tickrate
    return ticks

def ticksToText(ticks):
    songString = ""
    for tick in ticks:
        songString += NEW_TICK
        tickString = ""
        for pitch in tick:
            tickString += chr(pitch)
        if not tickString:
            tickString = REST
        songString += tickString
            
    return songString
        
    
def encodeMidiToText(filepath, writepath, track=DEFAULT_TRACK):
    filepath = os.path.abspath(filepath)
    writepath = os.path.abspath(writepath)
    midi_data = pretty_midi.PrettyMIDI(filepath)
    
    resolution = DEFAULT_RESOLUTION
    
    time_signature = midi_data.time_signature_changes[0]
    time_in_seconds, tempo_qpms = midi_data.get_tempo_changes()
    time = time_in_seconds[0]
    qpm = tempo_qpms[0]
    
    quarter_time = 60.0 / qpm
    tickrate = quarter_time / resolution
    
    instrument = midi_data.instruments[track]
    
    intervals = groupNotesByInterval(instrument)
    ticks = intervalsToTicks(intervals, tickrate)
    songText = ticksToText(ticks)
    
    with open(writepath, 'w') as f:
        f.write(songText)
