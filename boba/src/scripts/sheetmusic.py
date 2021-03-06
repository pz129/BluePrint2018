import numpy as np
# import matplotlib.pyplot as plt
# import IPython.display as ipd
# from IPython.display import display
# from ipywidgets import interact

import sys
# sys.path.append("../common")
from util import *
from music21 import *

# import fmp

# %matplotlib inline
# %matplotlib notebook
# plt.rcParams['figure.figsize'] = (12, 4)

' System arguments are in the form $python transcriber.py "file_name_here.wav" '
print "name: ", sys.argv[0]
if len(sys.argv) == 4:
	song_loc = sys.argv[1]
	song_output_location = sys.argv[2]
	song_name = sys.argv[3]
	print "song name:", song_loc
else:
	print "Not correct number of arguments"
	exit


' Load in the song name '
x = load_wav(song_loc) #load in the song
# plt.plot(x)
song_sum = np.sum(x)
avg = abs(song_sum) / len(x)
print avg
max_bound = avg * 800000
min_bound = avg * 300000
print min_bound, max_bound
sr = 22050 #sample rate
win_per_sec = 32
winsize = sr/win_per_sec #window size

num_win = len(x)/winsize

sheet = np.zeros((100, num_win)) # (rows, columns) row is frequency, column is the win idex
magftt = np.zeros((100, num_win))
print sheet.shape
# peaks = np.zeros(num_win)

# fft_timeline = np.zeros((100))

for win_idx in range(num_win):
	start = win_idx * winsize
	end = win_idx * winsize + winsize

	' set up, multiply by hanning curve and zpad '
	win = x[start:end]
	x_w = zpad(win * np.hanning(len(win)), winsize*2)

	' perform fft this will return contribution ' 
	ft = np.fft.rfft(x_w)

	' take abs and get rid of negatives '
	magft = np.abs(ft)

	for contrib in range(100):
		# print magft[contrib]
		' value to change'
		# sheet[contrib][win_idx] = 1
		magftt[contrib][win_idx]=magft[contrib]
		if magft[contrib] < min_bound:
			# print "herea"
			sheet[contrib][win_idx] = 0
		elif magft[contrib] > max_bound:
			# print "maxboudn", max_bound
			sheet[contrib][win_idx] = 2
		else:
			# print "herec"
			sheet[contrib][win_idx] = 1

# print sheet
# sheet = [[2, 1, 2]]
# ' 0 0 2 2 2 2 0 0 0 2 '
# sheet = np.array(sheet)
# print sheet

' remove 1s from the sheet music turning them into a 0 or 2 '
for freq_line in sheet:
	# print freq_line
	prev_is_two = False
	curr_is_two = False
	prev_idx = 0
	for idx in range(len(freq_line)):
		if freq_line[idx] == 2:
			if idx > 0 and freq_line[idx-1] == 1:
				curr_is_two = True
				if curr_is_two == True and prev_is_two == True:
					freq_line[prev_idx:idx] = 2
					prev_is_two = True
				else:
					freq_line[prev_idx:idx] = 0
					prev_is_two = False
			else:
				prev_is_two = True
			prev_idx = idx

		elif freq_line[idx] == 0:
			if idx > 0 and freq_line[idx-1] == 1:
				curr_is_two = False
				freq_line[prev_idx:idx] = 0
			prev_idx = idx
			prev_is_two = False
	# print freq_line

# print sheet
# print win_per_sec

# bpm = 120
transcribe_sheet = np.zeros((100, num_win/4))
transcribe_magftt= np.zeros((100, num_win/4))
result = np.zeros((num_win/4,2))
# print(transcribe_magftt)
# print(magftt)
# print(num_win)
' there will be num_win number of 0s and 2s which is numsec * sr '
' add in groups of 4 to get sixteenth notes '
for i in range(len(sheet[0])):
        for j in range(100):
                if sheet[j][i]==2:
                        transcribe_sheet[j][i/4]+=1
                transcribe_magftt[j][i/4]+=magftt[j][i]

#for freq_line_idx in range(len(sheet)):
#	freq_line = sheet[freq_line_idx]
#	for i in range(len(freq_line)/4):
#		start = i*4
#		end = i*4+4
#		total = 0
#		for num in freq_line[start:end]:
#			if num == 2:
#				total += 1
#		if total != 0:
#			print "total", total
#		transcribe_sheet[freq_line_idx][i] = total
np.set_printoptions(threshold='nan')
#print(transcribe_magftt)
#print(magftt)
# print(magftt.shape)
for i in range(len(transcribe_sheet[0])):
        bestFreq=0
        for j in range(100):
                if transcribe_magftt[j][i]>transcribe_magftt[bestFreq][i]:
                        bestFreq=j
        # print(bestFreq)
        #print("asdfadsf")
        result[i][0]=bestFreq
        result[i][1]=transcribe_sheet[bestFreq][i]

strm = stream.Stream()
strm.insert(0, metadata.Metadata())
strm.metadata.title = song_name
strm.metadata.composer = ""
lengthtot=0
resultsStrings= []
# print(len(result))
for i in range(len(result)):
        # print(i)
        #print(result[i][0])
        if(result[i][0]==0):
                result[i][0]+=1
        freq = bin_to_freq(result[i][0],sr,winsize)
        #print(freq)
        pitches = freq_to_pitch(freq)
        #print(pitches)
        note2=pitch_to_spn(int(round(pitches)))
        # print(result[i][1])
        if(result[i][1]<2):
                note2="-1"
        # print(note2)
        resultsStrings.append(note2)
                
for i in range(len(result)):
        lengthtot+=1
        if i!=0:
                if resultsStrings[i]!=resultsStrings[i-1] or result[i][1]<=3:
                        if resultsStrings[i-1]=="-1":
                                strm.append(note.Rest( quarterLength=0.25*lengthtot))
                        else:
                                strm.append(note.Note(resultsStrings[i-1], quarterLength=0.25*lengthtot))
                        lengthtot=0;

if lengthtot > 0:
        strm.append(note.Note(resultsStrings[i-1],quarterLength=0.25*lengthtot))

# strm.show()
fp = strm.write("musicxml", song_output_location)

# strm = stream.Stream()
# for vals in peaks:
# 	# print vals
# 	rest = False
# 	notes_in_chord = []
# 	' convert the set of peaks to frequencies '
# 	freqs = bin_to_freq(vals, sr, winsize) #peaks, sr, winsize

# 	' convert frequencies to pitches'
# 	pitches = freq_to_pitch(freqs)

# 	for pitch in pitches:
# 		print pitch
# 		'convert pitches to spn and add to chord '
# 		# print note.Note(pitch_to_spn(int(round(pitch))))
# 		note_to_add = pitch_to_spn(int(round(pitch)))
# 		if note_to_add == "-1":
# 			rest = True
# 		else:
# 			notes_in_chord.append(note.Note(note_to_add, quarterLength=1.5))

# 	if rest == False:
# 		' make chord and add it to strm '
# 		chord_value = chord.Chord(notes_in_chord)
# 		print chord_value
# 		strm.append(chord_value)
# 	else:
# 		strm.append(note.Rest())

# ' show/write strm'
# # strm.show()
# fp = strm.write("musicxml", "../sheets/score.xml")



# freqs = bin_to_freq(peaks, sr, winsize) #peaks, sr, winsize
# pitches = freq_to_pitch(freqs)


# strm = stream.Stream()
# for pitch in pitches:
# 	strm.append(note.Note(pitch_to_spn(int(round(pitch)))))

# strm.show()

#for now discard ending part, can add 1 to num_win instead
# print len(x)
