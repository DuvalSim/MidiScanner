import music21

t = music21.converter.parse("./output_files/exported.musicxml")

newScore = music21.stream.Score()


for idx, part in enumerate(t.parts):
    
    
    flat_part = part.flatten()
    # flat_part = part.copy()
    print(flat_part)
    flat_part.timeSignature = music21.meter.TimeSignature('4/4')
    # Only for the first part
    # if idx == 0:
    current_bpm = flat_part.getElementsByClass(music21.tempo.MetronomeMark)[0]
    new_bpm = music21.tempo.MetronomeMark(number=54)
    new_bpm.placement = "above"
    flat_part.replace(current_bpm, new_bpm)

    
    
    
    flat_part.makeNotation(inPlace=True)
    newScore.insert(0, flat_part)

newScore.write('musicxml', fp='./output_files/final.musicxml')