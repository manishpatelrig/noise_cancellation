import os

#referenceDirectory = "./reference_transcripts"
#transcriptDirectory = "./transcripts"

referenceDirectory = "./r1"
transcriptDirectory = "./t2"

#for i in range(745):
totalCount = 0
four = 0
one = 0
two = 0
six =0
eight=0
oneAbove = 0

for i in range(100):
    a = os.popen('python3 wer.py' + ' ' + referenceDirectory + '/' +  str(i) + '.txt' + ' ' +
              transcriptDirectory + '/' +  str(i) + '.txt').read()
    wer = a.split("\n")[3].split(":")[1][1:-1]
    wer_float = float(wer)/100
    if ( (wer_float >= 0) and (wer_float <= 0.2)):
        two = two + 1
    elif ((wer_float >= 0.21) and (wer_float <= 0.4)):
        four = four + 1
    elif ( (wer_float >= 0.41) and (wer_float <= 0.6)):
        six= six+ 1
    elif ((wer_float >= 0.61) and (wer_float <= 0.8)):
        eight = eight + 1
    elif ( (wer_float >= 0.81) and (wer_float <= 1.0)):
        one = one + 1
    else:
        oneAbove = oneAbove + 1
    #print(str(i) + " :" + str(wer_float))
    totalCount= totalCount + (wer_float)

print(two)
print(four)
print(six)
print(eight)
print(one)
print(oneAbove)
print(totalCount/100)