import csv
import os
import time
from datetime import datetime


def start_num(nfile_lines):
    num = 0
    for i in range(len(nfile_lines)):
        if nfile_lines[i].find('END OF HEADER') != -1:
            num = i + 1
    return num


def read_brdc(day, type_flag, year):
    if type_flag == 0:
        read_path = 'BRDC/GPS/' + str(year) + '/brdc' + str(day).zfill(3) + '0.' + str(year)[-2:] + 'n'
    else:
        read_path = 'BRDC/BEIDOU/' + str(year) + '/hour' + str(day).zfill(3) + '0.' + str(year)[-2:] + 'b'
    with open(read_path, 'r') as f:
        if f == 0:
            print("Unable to open the alamanc file!")
        else:
            print("Open the alamanc successfully")
        brdc_lines = f.readlines()
        f.close()
    return brdc_lines


def almanac_interpretation():
    loc_start = 4
    datetimeformat = ["%Y %m %d %H %M %S.%f", "%Y %m %d %H %M %S"]
    write_path = ['Almanac Interpretation/GPS/', 'Almanac Interpretation/BEIDOU/']
    constellation = ['GPS','BEIDOU']
    doy = time.localtime(time.time()).tm_yday - 1
    year = time.localtime(time.time()).tm_year
    for k in range(2):
        print("")
        print("Interpretation: " + constellation[k])
        loc_start = loc_start + k
        if k == 0:
            prn_count = list(range(1, 33))
        else:
            prn_count = list(range(1, 63))

        nfile_lines = read_brdc(doy, k, year)

        now_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        n_dic_list = []

        n_data_lines_nums = int((len(nfile_lines) - start_num(nfile_lines)) / 8)

        for j in range(n_data_lines_nums):

            skip_flag = 0
            n_dic = {}
            currentPRN = 0
            header_flag = 1
            for i in range(8):
                data_content = nfile_lines[start_num(nfile_lines) + 8 * j + i].replace('D', 'E')
                n_dic['Tuple_numbers'] = j + 1
                if i == 0:
                    n_dic['PRN'] = str(data_content[loc_start - 4:loc_start - 2])
                    currentPRN = int(n_dic['PRN'])
                    n_dic['epoch'] = data_content[loc_start - 1:loc_start + 18]
                    if k == 0:
                        date_temp = datetime.strptime('20' + n_dic['epoch'], datetimeformat[k])
                    else:
                        date_temp = datetime.strptime(n_dic['epoch'], datetimeformat[k])

                    if (now_midnight - date_temp).seconds < 3600 or (now_midnight - date_temp).seconds > 3 * 3600:
                        skip_flag = 1
                        break

                    n_dic['sx_clock_offset(s)'] = float(
                        (data_content.strip('\n')[loc_start + 18:loc_start + 37]))

                    n_dic['sx_clock_drift(s/s)'] = float((data_content.strip('\n')[loc_start + 37:loc_start + 56]))

                    n_dic['sx_clock_drift_speed(s/s*s)'] = float(
                        (data_content.strip('\n')[loc_start + 56:loc_start + 75]))
                if i == 1:
                    n_dic['IODE'] = float(
                        (data_content.strip('\n')[loc_start:loc_start + 18]))
                    n_dic['C_rs'] = float(
                        (data_content.strip('\n')[loc_start + 18:loc_start + 37]))
                    n_dic['n'] = float(
                        (data_content.strip('\n')[loc_start + 37:loc_start + 56]))
                    n_dic['M0'] = float(
                        (data_content.strip('\n')[loc_start + 56:loc_start + 75]))
                if i == 2:
                    n_dic['C_uc'] = float(
                        (data_content.strip('\n')[loc_start:loc_start + 18]))
                    n_dic['e'] = float(
                        (data_content.strip('\n')[loc_start + 18:loc_start + 37]))
                    n_dic['C_us'] = float(
                        (data_content.strip('\n')[loc_start + 37:loc_start + 56]))
                    n_dic['sqrt_A'] = float(
                        (data_content.strip('\n')[loc_start + 56:loc_start + 75]))
                if i == 3:
                    n_dic['TEO'] = float(
                        (data_content.strip('\n')[loc_start:loc_start + 18]))
                    n_dic['C_ic'] = float(
                        (data_content.strip('\n')[loc_start + 18:loc_start + 37]))
                    n_dic['OMEGA'] = float(
                        (data_content.strip('\n')[loc_start + 37:loc_start + 56]))
                    n_dic['C_is'] = float(
                        (data_content.strip('\n')[loc_start + 56:loc_start + 75]))

                if i == 4:
                    n_dic['I_0'] = float(
                        (data_content.strip('\n')[loc_start:loc_start + 18]))
                    n_dic['C_rc'] = float(
                        (data_content.strip('\n')[loc_start + 18:loc_start + 37]))
                    n_dic['w'] = float(
                        (data_content.strip('\n')[loc_start + 37:loc_start + 56]))
                    n_dic['OMEGA_DOT'] = float(
                        (data_content.strip('\n')[loc_start + 56:loc_start + 75]))
                if i == 5:
                    n_dic['IDOT'] = float(
                        (data_content.strip('\n')[loc_start:loc_start + 18]))
                    n_dic['L2_code'] = float(
                        (data_content.strip('\n')[loc_start + 18:loc_start + 37]))
                    n_dic['PS_week_num'] = float(
                        (data_content.strip('\n')[loc_start + 37:loc_start + 56]))

                if i == 6:
                    n_dic['sx_accuracy(m)'] = float(
                        (data_content.strip('\n')[loc_start:loc_start + 18]))
                    n_dic['sx_state'] = float(
                        (data_content.strip('\n')[loc_start + 18:loc_start + 37]))
                    n_dic['TGD'] = float(
                        (data_content.strip('\n')[loc_start + 37:loc_start + 56]))
                    n_dic['IODC'] = float(
                        (data_content.strip('\n')[loc_start + 56:loc_start + 75]))
            if not skip_flag:
                interpret_path = write_path[k] + str(doy) + '_' + str(currentPRN) + '.csv'
                if currentPRN in prn_count:
                    if os.path.exists(interpret_path):
                       os.remove(interpret_path)
                    with open(interpret_path, 'a+', newline='') as f:
                        header = ['Tuple_numbers', 'PRN', 'epoch', 'sx_clock_offset(s)', 'sx_clock_drift(s/s)',
                                  'sx_clock_drift_speed(s/s*s)', 'IODE',
                                  'C_rs', 'n', 'M0', 'C_uc', 'e', 'C_us', 'sqrt_A', 'TEO', 'C_ic', 'OMEGA', 'C_is',
                                  'I_0',
                                  'C_rc', 'w',
                                  'OMEGA_DOT', 'IDOT', 'L2_code', 'PS_week_num', 'L2_P_code', 'sx_accuracy(m)',
                                  'sx_state',
                                  'TGD',
                                  'IODC', 'X', 'Y', 'Z']
                        writer = csv.DictWriter(f, fieldnames=header)
                        if header_flag:
                            writer.writeheader()
                        writer.writerow(n_dic)
                    f.close()
                    prn_count.remove(currentPRN)
            n_dic_list.append(n_dic)
        if len(prn_count) != 0:
            print(prn_count)
        else:
            print("ALL INTERPRETED")
    return write_path
