import sys
import numpy as np
import pandas as pd
import mne
from mne.time_frequency import psd_multitaper
from brainflow.board_shim import BoardIds, BoardShim
import csv
import datetime as dt
from mne.datasets import somato
from mne.baseline import rescale
from mne.stats import bootstrap_confidence_interval
import matplotlib.pyplot as plt
import pandas as pd


check = True
numpy_list = []
direction_list = ['forward', 'right', 'backward', 'left', 'stop']
ch_list = ['TLow_', 'T_', 'ALow_', 'A_', 'BLow_', 'B_', 'GLow_', 'G_']
df = pd.read_csv("EEG-obtain-data-master/temp_data.csv")
loop_list = []
loop_list.append(df[df['Direction'] == 'forward'])
loop_list.append(df[df['Direction'] == 'right'])
loop_list.append(df[df['Direction'] == 'backward'])
loop_list.append(df[df['Direction'] == 'left'])
loop_list.append(df[df['Direction'] == 'stop'])
counter = 0
for i in loop_list:
    
    df = i
    df = df.drop('Direction', 1)
    dataEEg = df.to_numpy()
    dataEEg = dataEEg[0:len(dataEEg), :16]
    dataEEg = dataEEg / 1000000

    print(len(dataEEg))

    looping = 1
    for m in range(looping):
        window_number = len(dataEEg) // looping
        EegData = dataEEg[(m * window_number):((m * window_number) + window_number), :]
        dataArrX = EegData
        dataArrX = np.transpose(dataArrX)

        if True:
            n_channels = 16
            trial_window = len(dataEEg) // looping  # number of data points per trial
            bad_channel_threshold = sys.maxsize
            bad_trial_threshold = sys.maxsize

        number_of_trials = int(1)

        if True:
            channel_names = ['Fp1', 'Fp2', 'C3', 'C4', 'P7', 'P8', 'O1', 'O2', 'F7', 'F8', 'F3', 'F4', 'T7', 'T8', 'P3',
                             'P4']

        sfreq = 128

        channel_types = 'eeg'  # could be list corresponding one channel type for one channel name
        montage = None
        info = mne.create_info(channel_names, sfreq, channel_types, montage)
        info['description'] = 'eeg dataset'
        custom_raw = mne.io.RawArray(dataArrX, info)

        custom_raw.filter(l_freq=1, h_freq=45.0,
                          l_trans_bandwidth=0.00099)  # Be careful about the freqs and l_trans_bandwidth

        filtered_data = custom_raw._data

        epoch_info = mne.create_info(
            ch_names=channel_names,
            ch_types=channel_types,
            sfreq=sfreq
        )
        if True:
            tmin = -0.25
            baseline = (-0.25, 0)

        data = filtered_data[:, 0:(trial_window)]
        data = data.reshape(n_channels, number_of_trials, trial_window)
        data = np.transpose(data, axes=[1, 0, 2])
        custom_epochs = mne.EpochsArray(data, epoch_info, None, 0, None)

        list_of_var_means = []
        array_of_vars = np.zeros((n_channels, number_of_trials), dtype=np.float32)
        for chNum in range(n_channels):
            for k in range(number_of_trials):
                trial = custom_epochs._data[k][chNum]
                array_of_vars[chNum][k] = int(np.var(trial))
            mean_of_allVariances = np.mean(array_of_vars[chNum][:],
                                           dtype=np.float32)  # mean of all variances of all trials in a channel
            list_of_var_means.append(mean_of_allVariances)
            if mean_of_allVariances > bad_channel_threshold:  # Bad channel
                info['bads'].append(channel_names[chNum])

        pick_list = mne.pick_types(custom_raw.info, eeg=True, exclude='bads')
        n_jobs = 1
        isMultitaper = False
        if isMultitaper:
            psdsTx, freqsTx = psd_multitaper(custom_epochs, fmin=6, fmax=11, normalization='length', picks=pick_list,
                                             n_jobs=1)
            psdsT, freqsT = psd_multitaper(custom_epochs, fmin=5, fmax=8, normalization='length', picks=pick_list,
                                           n_jobs=1)
            psdsA, freqsA = psd_multitaper(custom_epochs, fmin=8, fmax=13, normalization='length', picks=pick_list,
                                           n_jobs=1)
            psdsAL, freqsAL = psd_multitaper(custom_epochs, fmin=8, fmax=10, normalization='length', picks=pick_list,
                                             n_jobs=1)
            psdsB, freqsB = psd_multitaper(custom_epochs, fmin=14, fmax=27, normalization='length', picks=pick_list,
                                           n_jobs=1)
            psdsG, freqsG = psd_multitaper(custom_epochs, fmin=30, fmax=45, normalization='length', picks=pick_list,
                                           n_jobs=1)


        else:
            frequency_map = list()
            iter_freqs = [
                ('thetaLow', 4.0, 5.5),
                ('thetaHigh', 5.5, 7),
                ('alphaLow', 7, 10),
                ('alphaHigh', 10, 13),
                ('betaLow', 14, 22),
                ('betaHigh', 22, 30),
                ('gammaLow', 31, 38),
                ('gammaHigh', 38, 45),

            ]
            c = 0
            for band, fmin, fmax in iter_freqs:
                band_data = custom_raw
                band_data.filter(fmin, fmax, n_jobs=1, )  # use more jobs to speed up.

                filtered_data2 = band_data.get_data()
                data = filtered_data2.reshape(n_channels, number_of_trials, trial_window)
                data = np.transpose(data, axes=[1, 0, 2])
                custom_epochs = mne.EpochsArray(data, epoch_info, None, tmin, None)

                frequency_map.append(((band, fmin, fmax), custom_epochs.average()))
                columns = []
                for z in ["Fz", "C3", "Cz", "C4", "Pz", "PO7", "Oz", "PO8", "F5", "F7", "F3", "F1", "F2", "F4", "F6",
                          "F8"]:
                    columns.append((ch_list[c] + z))

                print("epochs are")
                print(band)
                print(len(custom_epochs))
                for epoch in custom_epochs:
                    epoch = epoch.transpose()
                df = pd.DataFrame(epoch,
                                  columns=columns)
                if band == 'thetaLow':
                    df['Direction'] = direction_list[counter]
                print(df)
                df.to_csv("temp_" + band + ".csv", mode='a', header=check, index=False)
                del custom_epochs
                c += 1
    check = None
    counter += 1