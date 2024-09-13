import numpy as np
import math as m
import matplotlib.pyplot as plt
import time
from datetime import datetime

# plt.ion()
TIME_DIVISION = True
pi = m.pi
pattern_graph = []
sweeping_AZ = [-50 / 180 * pi, -30 / 180 * pi, -10 / 180 * pi, 10 / 180 * pi, 30 / 180 * pi, 50 / 180 * pi]

frequency = 1.57542e9
c = 3e8
lamda = c / frequency
dy = 0.084
dx = 0.084
x_element_num = 8
y_element_num = 8

time_end = 1e6
time_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
time_duration = 10

fig, axs = plt.subplots(2, 2)


def calculate_inc_phase(EL, AZ):
    incident_phase = np.random.rand(x_element_num, y_element_num)
    for j in range(y_element_num):
        for i in range(x_element_num):
            incident_phase[j, i] = (2 * pi / lamda * dy * (m.sin(EL) * j + m.cos(EL) * m.sin(AZ) * i))

    return incident_phase


def read_inc(filename_AZ, filename_EL):
    AZ_set = np.loadtxt(filename_AZ, delimiter=",", skiprows=0)
    EL_set = np.loadtxt(filename_EL, delimiter=",", skiprows=0)
    AZ_set = np.delete(AZ_set, 0, axis=1)
    EL_set = np.delete(EL_set, 0, axis=1)
    return AZ_set, EL_set


def phase_pattern(d_EL, d_AZ, incident_phase):
    phase_setting = np.random.rand(y_element_num, x_element_num)
    phase_ideal = np.random.rand(y_element_num, x_element_num)
    for i in range(x_element_num):
        for j in range(y_element_num):
            phase_ideal[j][i] = (2 * pi / lamda * (
                    m.cos(d_EL) * m.sin(d_AZ) * dy * (j - y_element_num + 0.5) + m.cos(d_EL) * m.cos(d_AZ) * (
                    i - x_element_num + 0.5) * dx) - incident_phase[j, i]
                                 ) % (2 * pi)

            if phase_ideal[j][i] < pi / 2 or phase_ideal[j][i] > 3 * pi / 2:
                phase_setting[j][i] = 0
            else:
                phase_setting[j][i] = 1
    return phase_ideal, phase_setting


def phase_update(offline_flag):
    if offline_flag:
        num_day = 257
    else:
        num_day = time.localtime(time.time()).tm_yday
    EL_path = "AoA Prediction/EL_" + str(num_day) + ".csv"
    AZ_path = "AoA Prediction/AZ_" + str(num_day) + ".csv"
    time_deviation = time.time() - time_start
    AZ_set, EL_set = read_inc(AZ_path, EL_path)
    while time_deviation < time_end:
        time_count = m.floor(time_deviation / time_duration)
        AZ_record = AZ_set[time_count][:32]
        EL_record = EL_set[time_count][:32]
        selected = np.argsort(EL_record)
        while m.floor(time_deviation / time_duration) == time_count:
            for i in range(len(sweeping_AZ)):
                for ris in range(4):
                    print(time_count)
                    print(' ')
                    print("TIME:" + str(datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")))
                    print("RIS:" + str(ris))
                    print("Selection:")
                    print(EL_record[selected[-ris - 1]] / pi * 180)
                    print(AZ_record[selected[-ris - 1]] / pi * 180)

                    if selected[-ris - 1] + 1 > 32:
                        print("BEIDOU: " + str(selected[-ris - 1] + 1 - 32))
                    else:
                        print("GPS: " + str(selected[-ris - 1] + 1))

                    incident_phase = calculate_inc_phase(EL_record[selected[-ris - 1]],
                                                         AZ_record[-ris - 1] - 90 / 180 * pi)

                    phase_ideal, phase_setting = phase_pattern(0, sweeping_AZ[i], incident_phase)
                    # Send control signal to the imu which controls each of the meta-atom on the metasurface
                    # ser_control(phase_setting)
                    # print(phase_setting)
                    axs[int(ris / 2), ris % 2].pcolor(phase_setting, cmap="pink")
                    axs[int(ris / 2), ris % 2].set_aspect('equal')
                    plt.draw()
                    plt.pause(0.1)
                time.sleep(1 / len(sweeping_AZ))

            time_deviation = time.time() - time_start
    plt.show()
