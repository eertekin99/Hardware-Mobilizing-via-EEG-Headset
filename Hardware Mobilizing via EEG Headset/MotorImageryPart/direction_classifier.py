import argparse
import time
import numpy as np
import brainflow
import os.path
import statistics
import time
import pandas as pd
import urllib.request
import requests
import logging
import matplotlib
import matplotlib.pyplot as plt
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, DetrendOperations
from pylsl import StreamInfo, StreamOutlet
import pickle
from statistics import mode
from sklearn.svm import OneClassSVM

board = None
board_shim = None
eeg_chan = None


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
def get_data():
    global board_shim
    eeg_channels = BoardShim.get_eeg_channels (2)
    sampling_rate = BoardShim.get_sampling_rate(2)
    data = board_shim.get_board_data()

    data_list_alpha = []
    data_list_beta = []
    data_list_gamma = []
    data_list_theta = []

    data_list_alphaLow = []
    data_list_betaLow = []
    data_list_gammaLow = []
    data_list_thetaLow = []

    for count, channel in enumerate(eeg_channels):
       
        DataFilter.detrend(data[channel], DetrendOperations.CONSTANT.value)
        #FILTERING WITH BANDPASS // BETWEEN 1-46HZ.
        DataFilter.perform_bandpass(data[channel], sampling_rate, 23.5, 45, 3,
                                    FilterTypes.CHEBYSHEV_TYPE_1.value, 0.2)
        #50HZ Europe Electricity
        DataFilter.perform_bandstop(data[channel], sampling_rate, 50.0, 4, 4,
                                    FilterTypes.CHEBYSHEV_TYPE_1.value, 0.2)
        #DENOISING THE CHANNELS
        DataFilter.perform_wavelet_denoising(data[channel], 'coif3', 3)

        nfft = DataFilter.get_nearest_power_of_two(64)
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


        while i < len(data[channel]):
            x = i + increment_number
            if increment_number > len(data[channel]) - i or x >= len(data[channel]):
                x = len(data[channel])
            
            if nfft > len(data[channel]) - i:
                break

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


            alpha_list.append(band_power_alphaHigh)
            beta_list.append(band_power_betaHigh)
            gamma_list.append(band_power_gammaHigh)
            theta_list.append(band_power_thetaHigh)

            alphaLow_list.append(band_power_alphaLow)
            betaLow_list.append(band_power_betaLow)
            gammaLow_list.append(band_power_gammaLow)
            thetaLow_list.append(band_power_thetaLow)
            i = x

        data_list_alpha.append(alpha_list)
        data_list_alphaLow.append(alphaLow_list)
        data_list_beta.append(beta_list)
        data_list_betaLow.append(betaLow_list)
        data_list_gamma.append(gamma_list)
        data_list_gammaLow.append(gammaLow_list)
        data_list_theta.append(theta_list)
        data_list_thetaLow.append(thetaLow_list)

    df1 = pd.DataFrame(data_list_alpha)
    df2 = pd.DataFrame(data_list_beta)
    df3 = pd.DataFrame(data_list_gamma)
    df4 = pd.DataFrame(data_list_theta)

    df5 = pd.DataFrame(data_list_alphaLow)
    df6 = pd.DataFrame(data_list_betaLow)
    df7 = pd.DataFrame(data_list_gammaLow)
    df8 = pd.DataFrame(data_list_thetaLow)

  
    frames = [df1, df5, df2, df6, df3, df7, df4, df8]
    df = pd.concat(frames, axis=0).T
    return df


def main(file):
    loaded_model = pickle.load(open(file, 'rb'))
    start_connection()
    start = time.time()
    ipvar = "http://192.168.43.128:8000"
    direction = "stop"
    request_check=False
    requests.get(ipvar + '/run/?action=stop',timeout=1)
    empty_buffer()
    while True:
        end = time.time()
        if int(end - start) >= 2.5:
            request_check = True
            df = get_data()
            print("------------------------------")
            result = loaded_model.predict(df)

            # Getting the mode of the list, if all values are different then uses the last one.
            a = mode(result)
            l = list(result)
            if l.count(a) == 1:
                print(result[len(result)-1])
                direction=result[len(result)-1]

            else:
                direction=a
                print(a)

            empty_buffer()
            start = time.time()
            request_check=True

        if True:
            print(direction)
            if direction == "right":
                print("MOVEMENT: RIGHT")
                requests.get(ipvar + '/run/?action=fwright')
                requests.get(ipvar + '/run/?action=forward')
                requests.get(ipvar + '/run/?action=forward')
                requests.get(ipvar + '/run/?action=forward')

                requests.get(ipvar + '/run/?action=fwstraight')
                requests.get(ipvar + '/run/?action=stop')

            elif direction == "left":
                print("MOVEMENT: LEFT")
                requests.get(ipvar + '/run/?action=fwleft')
                requests.get(ipvar + '/run/?action=forward')
                requests.get(ipvar + '/run/?action=forward')
                requests.get(ipvar + '/run/?action=forward')

                requests.get(ipvar + '/run/?action=fwstraight')
                requests.get(ipvar + '/run/?action=stop')

            elif direction == "forward":
                print("MOVEMENT: FORWARD")
                requests.get(ipvar + '/run/?action=forward')
                requests.get(ipvar + '/run/?action=forward')
                requests.get(ipvar + '/run/?action=forward')

                requests.get(ipvar + '/run/?action=stop')

            elif direction == "backward":
                print("MOVEMENT: BACKWARD")
                requests.get(ipvar + '/run/?action=backward')
                requests.get(ipvar + '/run/?action=backward')
                requests.get(ipvar + '/run/?action=backward')


                requests.get(ipvar + '/run/?action=stop')

            elif direction == "stop":
                requests.get(ipvar + '/run/?action=stop')
                print("NO DIRECTION")
                requests.get(ipvar + '/run/?action=fwstraight')


#main()