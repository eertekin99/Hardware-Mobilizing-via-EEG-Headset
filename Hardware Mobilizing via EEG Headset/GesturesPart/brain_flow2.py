import argparse
import numpy as np
import brainflow
import os.path
import pandas as pd
import urllib.request
import requests
import logging
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, DetrendOperations

board = None
board_shim = None
eeg_chan = None
check = not os.path.exists('temp_alphaHigh.csv')
print(check)

def empty_buffer():
    data = board_shim.get_board_data()

def start_connection():
    global board_shim
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    # use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
    parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                        default=0)
    parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
    parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                        default=0)
    parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
    parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='COM3')
    parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
    parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
    parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='')
    parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')
    parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                        required=False, default=2)
    parser.add_argument('--file', type=str, help='file', required=False, default='')
    args = parser.parse_args()

    params = BrainFlowInputParams()
    params.ip_port = args.ip_port
    params.serial_port = args.serial_port
    params.mac_address = args.mac_address
    params.other_info = args.other_info
    params.serial_number = args.serial_number
    params.ip_address = args.ip_address
    params.ip_protocol = args.ip_protocol
    params.timeout = args.timeout
    params.file = args.file

    try:
        board_shim = BoardShim(args.board_id, params)
        board_shim.prepare_session()
        board_shim.start_stream(450000, args.streamer_params)
    except BaseException:
        logging.warning('Exception', exc_info=True)
    finally:
        logging.info('End')
        if board_shim.is_prepared():
            logging.info('Releasing session')


# 1 - 45 frequency
def get_data(direction):
    global board_shim, check
    eeg_channels = BoardShim.get_eeg_channels (2)
    sampling_rate = BoardShim.get_sampling_rate(2)
    print("IMPORTANT!!!!!!")
    print(sampling_rate)
    print(eeg_channels)
    data = board_shim.get_board_data()

    data_list = []
    data_list_alpha = []
    data_list_beta = []
    data_list_gamma = []
    data_list_theta = []

    data_list_alphaLow = []
    data_list_betaLow = []
    data_list_gammaLow = []
    data_list_thetaLow = []

    for count, channel in enumerate(eeg_channels):

        #DETREND
        DataFilter.detrend(data[channel], DetrendOperations.CONSTANT.value)

        #FILTERING WITH BANDPASS // BETWEEN 1-46HZ.
        DataFilter.perform_bandpass(data[channel], sampling_rate, 23.5, 45, 3,
                                    FilterTypes.CHEBYSHEV_TYPE_1.value, 0.2)

        #BANDSTOPPING THE NOISE THAT COMES FROM EUROPE ELECTRICAL POWER WHICH 50HZ
        DataFilter.perform_bandstop(data[channel], sampling_rate, 50.0, 4, 4,
                                    FilterTypes.CHEBYSHEV_TYPE_1.value, 0.2)

        #DENOISING THE CHANNELS
        DataFilter.perform_wavelet_denoising(data[channel], 'coif3', 3)



        i = 0
        increment_number = 64
        theta_list = []
        alpha_list = []
        beta_list = []
        gamma_list = []

        thetaLow_list = []
        alphaLow_list = []
        betaLow_list = []
        gammaLow_list = []

        nfft = DataFilter.get_nearest_power_of_two(64)

        print("LENGTH",len(data[channel]))
        while i < len(data[channel]):
            x = i + increment_number
            if increment_number > len(data[channel])-i or x >= len(data[channel]):
                x = len(data[channel])
            print(nfft)
            if nfft > len(data[channel])-i:
                break

            print("---------------------------------------------------")
            print("INDEXES ARE HERE !!!!!!!")
            print(i,x)
            print(nfft,sampling_rate)
            print("---------------------------------------------------")

            psd = DataFilter.get_psd_welch(data[channel][i:x], nfft, nfft // 2, 128,
                                               brainflow.WindowFunctions.BLACKMAN_HARRIS.value)

            band_power_thetaLow = DataFilter.get_band_power(psd, 4.0, 5.5)
            band_power_thetaHigh = DataFilter.get_band_power(psd, 5.5, 7.0)
            band_power_alphaLow = DataFilter.get_band_power(psd, 7.0, 10.0)
            band_power_alphaHigh = DataFilter.get_band_power(psd, 10.0, 13.0)
            band_power_betaLow = DataFilter.get_band_power(psd, 14.0, 22.0)
            band_power_betaHigh = DataFilter.get_band_power(psd, 22.0, 30.0)
            band_power_gammaLow = DataFilter.get_band_power(psd, 31.0, 38.0)
            band_power_gammaHigh = DataFilter.get_band_power(psd, 38.0, 45.0)

            theta_list.append(band_power_thetaHigh)
            alpha_list.append(band_power_alphaHigh)
            beta_list.append(band_power_betaHigh)
            gamma_list.append(band_power_gammaHigh)
            thetaLow_list.append(band_power_thetaLow)
            alphaLow_list.append(band_power_alphaLow)
            betaLow_list.append(band_power_betaLow)
            gammaLow_list.append(band_power_gammaLow)
            i = x

        #High values are assigned
        data_list_theta.append(theta_list)
        data_list_alpha.append(alpha_list)
        data_list_beta.append(beta_list)
        data_list_gamma.append(gamma_list)

        #Low values are assigned
        data_list_thetaLow.append(thetaLow_list)
        data_list_alphaLow.append(alphaLow_list)
        data_list_betaLow.append(betaLow_list)
        data_list_gammaLow.append(gammaLow_list)

        data_list.append(data[channel].tolist())


    #ALL DATA ARE COLLECTED INSIDE OF THIS PART
    df = pd.DataFrame(data_list,
                      index=['Fp1','Fp2','C3','C4','P7','P8','O1','O2','F7','F8','F3','F4','T7','T8','P3','P4']).T
    df['Direction'] = direction
    df.to_csv("temp_data.csv", mode='a', header=check,index=False)

    #ALPHAS ARE COLLECTED INSIDE THIS
    df_alpha = pd.DataFrame(data_list_alpha,
                      index=['A_Fp1','A_Fp2','A_C3','A_C4','A_P7','A_P8','A_O1','A_O2','A_F7','A_F8','A_F3','A_F4','A_T7','A_T8','A_P3','A_P4']).T
    df_alpha.to_csv("temp_alphaHigh.csv", mode='a', header=check,index=False)


    # LOW ALPHAS ARE COLLECTED INSIDE THIS
    df_alphaLow = pd.DataFrame(data_list_alphaLow,
                            index=['ALow_Fp1','ALow_Fp2','ALow_C3','ALow_C4','ALow_P7','ALow_P8','ALow_O1','ALow_O2','ALow_F7','ALow_F8','ALow_F3','ALow_F4','ALow_T7','ALow_T8','ALow_P3','ALow_P4']).T
    df_alphaLow.to_csv("temp_alphaLow.csv", mode='a', header=check, index=False)


    # BETAS ARE COLLECTED INSIDE THIS
    df_beta = pd.DataFrame(data_list_beta,
        index=['B_Fp1','B_Fp2','B_C3','B_C4','B_P7','B_P8','B_O1','B_O2','B_F7','B_F8','B_F3','B_F4','B_T7','B_T8','B_P3','B_P4']).T
    df_beta.to_csv("temp_betaHigh.csv", mode='a', header=check,index=False)


    #Low BETA
    df_betaLow = pd.DataFrame(data_list_betaLow,
                           index=['BLow_Fp1','BLow_Fp2','BLow_C3','BLow_C4','BLow_P7','BLow_P8','BLow_O1','BLow_O2','BLow_F7','BLow_F8','BLow_F3','BLow_F4','BLow_T7','BLow_T8','BLow_P3','BLow_P4']).T
    df_betaLow.to_csv("temp_betaLow.csv", mode='a', header=check, index=False)


    #GAMMAS ARE COLLECTED INSIDE THIS
    df_gamma = pd.DataFrame(data_list_gamma,
                           index=['G_Fp1','G_Fp2','G_C3','G_C4','G_P7','G_P8','G_O1','G_O2','G_F7','G_F8','G_F3','G_F4','G_T7','G_T8','G_P3','G_P4']).T
    df_gamma.to_csv("temp_gammaHigh.csv", mode='a', header=check,index=False)


    #LOWGAMMAS ARE COLLECTED INSIDE THIS
    df_gammaLow = pd.DataFrame(data_list_gammaLow,
                           index=['GLow_Fp1','GLow_Fp2','GLow_C3','GLow_C4','GLow_P7','GLow_P8','GLow_O1','GLow_O2','GLow_F7','GLow_F8','GLow_F3','GLow_F4','GLow_T7','GLow_T8','GLow_P3','GLow_P4']).T
    df_gammaLow.to_csv("temp_gammaLow.csv", mode='a', header=check,index=False)


    df_theta = pd.DataFrame(data_list_theta,
                            index=['T_Fp1','T_Fp2','T_C3','T_C4','T_P7','T_P8','T_O1','T_O2','T_F7','T_F8','T_F3','T_F4','T_T7','T_T8','T_P3','T_P4']).T
    df_theta.to_csv("temp_thetaHigh.csv", mode='a', header=check,index=False)


    df_thetaLow = pd.DataFrame(data_list_thetaLow,
                            index=['TLow_Fp1','TLow_Fp2','TLow_C3','TLow_C4','TLow_P7','TLow_P8','TLow_O1','TLow_O2','TLow_F7','TLow_F8','TLow_F3','TLow_F4','TLow_T7','TLow_T8','TLow_P3','TLow_P4']).T
    df_thetaLow['Direction'] = direction
    df_thetaLow.to_csv("temp_thetaLow.csv", mode='a', header=check,index=False)


    if check:
        check = False


    board_shim.get_board_data()
