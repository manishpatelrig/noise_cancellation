# Importing required packages.
import numpy as np
from pyAudioAnalysis import audioSegmentation as aseg
import os
from scipy.io import wavfile
import librosa as lr
import requests
import warnings
import logmmse

warnings.filterwarnings('ignore')
# directoryPath       : Directory path for input audio files.
# outputDirectory     : Output Directory where the filtered Primary Speaker's audio files will be saved.
# transcriptDirectory : Output Directory where the speech to text transcript of Primary Speaker will be saved.
directoryPath = input("Enter the Directory Path for input audio files :")
outputDirectory = input("Enter the Directory where you wish to save filtered Primary Speaker audio files :")
transcriptDirectory = input("Enter the Directory where you wish to save text Transcript of output files : ")

# Creating Output Directories at path specified by user.
os.mkdir(outputDirectory)
os.mkdir(transcriptDirectory)

# Lists all files in the current directory
allfiles = os.listdir(directoryPath)

# iterate over all files in the current directory
for item in allfiles:
    if item.endswith('.mp3') or item.endswith('.flac') or item.endswith('.wav') or item.endswith('.ogg') or item.endswith('.m4a'):
        file_name = item.split('.')
        audioFilePath = directoryPath + "/" + item
        # Loading individual audio file using Librosa
        audioData, framerate = lr.load(audioFilePath, res_type='kaiser_fast')
        data = lr.to_mono(audioData)
        # Removing small frequency noise from the file
        temporaryProcessedData = logmmse.base.logmmse(data, framerate, output_file="b.wav", initial_noise=6, window_size=0,
                                 noise_threshold=0.15)
        framerate, data = wavfile.read("b.wav")
        tempAudioData = np.empty_like(data)
        tempAudioData[:] = data
        sum_amp = 0
        for i in tempAudioData:
            sum_amp += abs(i)
        sum_amp = sum_amp / tempAudioData.size
        for i in range(tempAudioData.size):
            if tempAudioData[i] < sum_amp:
                tempAudioData[i] = 0
        temporaryProcessedData = wavfile.write("c.wav", framerate, tempAudioData)

        tempAudioData = np.empty_like(data)
        tempAudioData[:] = data
        step_size = 0.1
        frameset_to_take = int(framerate * step_size)
        ctr = np.zeros(10)
        amp_sum = np.zeros(10)
        amp_cnt = np.zeros(10)
        amp_mean = np.zeros(10)
        counter = 0
        try:
            # Segmentation of Audio file based on amplitude of voice using supervised clustering
            temp = aseg.speaker_diarization("c.wav", 2, mid_window=0.1, mid_step=0.1, short_window=0.1, lda_dim=0,
                                            plot_res=False)
            # Finding mean amplitude of each identified speaker
            for k in range(temp.size):
                for l in range(frameset_to_take):
                    if counter < data.size:
                        if data.ndim == 2:
                            amp_sum[int(temp[k])] += abs(data[int(counter), 0])
                        else:
                            amp_sum[int(temp[k])] += abs(data[int(counter)])
                        amp_cnt[int(temp[k])] += 1
                        counter += 1
            for m in range(10):
                if amp_cnt[m] != 0:
                    amp_mean[m] = amp_sum[m] / amp_cnt[m]
            maxm_amp = 0
            for i in range(10):
                if amp_mean[i] > amp_mean[maxm_amp]:
                    maxm_amp = i

            z = np.empty_like(data)
            z[:] = tempAudioData
            if z.ndim == 2:
                z = np.delete(tempAudioData, 1, 1)
                z = z.flatten()
            counter = 0
            # Removing noise whose amplitude is smaller than half the mean amplitude of complete audio
            for k in range(temp.size):
                for l in range(frameset_to_take):
                    if counter < data.size:
                        if (temp[k] != maxm_amp):
                            if (amp_mean[int(temp[k])] < 0.5 * sum_amp):
                                z[counter] = 0
                    counter += 1
        except:
            pass
        # Saving the primary speaker audio into the output directory
        t = wavfile.write( outputDirectory + "/" +  file_name[0] + ".wav", framerate, tempAudioData)
        # Removing intermittent genearated audio files
        os.remove("b.wav")
        os.remove("c.wav")
        # API related to ASR
        headers = {'Authorization': 'Token 3715119fd7753d33bedbd3c2832752ee7b0a10c7'}
        data = {'user': '310', 'language': 'HI'}
        files = {'audio_file': open(outputDirectory + "/" + file_name[0] + '.wav', 'rb')}
        url = 'https://dev.liv.ai/liv_transcription_api/recordings/'
        res = requests.post(url, headers=headers, data=data, files=files)
        t = res.json()
        # Handling ASR returned results and saving it into transcripts
        if "transcriptions" in t:
            with open(transcriptDirectory + "/" + file_name[0] + ".txt", 'w') as output_file:
                output_file.write(t['transcriptions'][0]['utf_text'])
        else:
            with open(transcriptDirectory + "/" + file_name[0] + ".txt", 'w') as output_file:
                output_file.write("")

