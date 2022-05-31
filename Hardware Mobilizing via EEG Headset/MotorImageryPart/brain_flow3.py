import argparse
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
check = not os.path.exists('temp_data.csv')


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


def get_data(direction):
    global board_shim, check
    eeg_channels = BoardShim.get_eeg_channels(2)
    sampling_rate = BoardShim.get_sampling_rate(2)
    data = board_shim.get_board_data()
    data_list = []

    for count, channel in enumerate(eeg_channels):
        DataFilter.detrend(data[channel], DetrendOperations.CONSTANT.value)
        DataFilter.perform_bandpass(data[channel], sampling_rate, 23.5, 45, 3,
                                    FilterTypes.CHEBYSHEV_TYPE_1.value, 0.2)
        DataFilter.perform_bandstop(data[channel], sampling_rate, 50.0, 4, 4,
                                    FilterTypes.CHEBYSHEV_TYPE_1.value, 0.2)
        DataFilter.perform_wavelet_denoising(data[channel], 'coif3', 3)
        data_list.append(data[channel].tolist())


    df = pd.DataFrame(data_list,
                      index=["Fz", "C3", "Cz", "C4", "Pz", "PO7", "Oz", "PO8", "F5", "F7", "F3", "F1", "F2", "F4", "F6",
                             "F8"]).T
    df['Direction'] = direction
    df.to_csv("temp_data.csv", mode='a', header=check, index=False)
    if check:
        check = False
    board_shim.get_board_data()