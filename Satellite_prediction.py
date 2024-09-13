import csv
import time
import os
from coordinate_parse import *

LEAP_SECONDS = 18


# X0, Y0, Z0 = -2172973.2573146434, 4387015.552043409, 4074525.4712238107
# angle_window_N = 90 / 180 * pi


def satellite_prediction(interpret_path, flag_beidou, X0, Y0, Z0, angle_window_N):
    AZ_set = []
    EL_set = []
    t_bit = flag_beidou * 2
    prediction_t = np.linspace(0, 24 * 60 * 60, 24 * 60 * 6 + 1)

    if not os.path.exists(interpret_path):
        print("NONE")
        return
    with open(interpret_path, 'rt') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            PRN = str(row["PRN"])
            TIME = row["epoch"]
            year = int(TIME.strip('\n')[0:2 + t_bit])

            month = int(TIME.strip('\n')[2 + t_bit:5 + t_bit])

            day = int(TIME.strip('\n')[5 + t_bit:8 + t_bit])

            hour = int(TIME.strip('\n')[8 + t_bit:11 + t_bit])
            minute = int(TIME.strip('\n')[11 + t_bit:14 + t_bit])
            second = int(TIME.strip('\n')[14 + t_bit:17 + t_bit])

            a_0 = float(row["sx_clock_offset(s)"])
            a_1 = float(row["sx_clock_drift(s/s)"])
            a_2 = float(row["sx_clock_drift_speed(s/s*s)"])
            IODE = float(row["IODE"])
            C_rs = float(row["C_rs"])
            δn = float(row["n"])
            M0 = float(row["M0"])
            C_uc = float(row["C_uc"])
            e = float(row["e"])
            C_us = float(row["C_us"])
            sqrt_A = float(row["sqrt_A"])
            TEO = float(row["TEO"])
            C_ic = float(row["C_ic"])
            OMEGA = float(row["OMEGA"])
            C_is = float(row["C_is"])
            I_0 = float(row["I_0"])
            C_rc = float(row["C_rc"])
            w = float(row["w"])
            OMEGA_DOT = float(row["OMEGA_DOT"])
            IDOT = float(row["IDOT"])
            L2_code = float(row["L2_code"])
            PS_week_num = float(row["PS_week_num"])
            TGD = float(row["TGD"])
            IODC = float(row["IODC"])

    csvfile.close()

    if flag_beidou == 0:
        # convert to cst
        hour = hour + 8
        if hour > 24:
            day = day + 1
            hour = hour % 24
        ts_start = "20" + str(year) + "-" + str(month) + "-" + str(day) + " " + str(hour) + ":" + str(
            minute) + ":" + str(second)
    else:
        ts_start = str(year) + "-" + str(month) + "-" + str(day) + " " + str(hour) + ":" + str(
            minute) + ":" + str(second)

    ts_start = int(time.mktime(time.strptime(ts_start, "%Y-%m-%d %H:%M:%S")))
    gps_week, gps_day, gps_seconds, _ = utc_to_gps_week_seconds(ts_start)
    t_oc = gps_seconds
    t1 = prediction_t
    second_start = (day - 1) * 24 * 3600 + hour * 3600 + minute * 60 + second
    day_start = datetime.datetime.now().day
    time_deviation = day_start * 24 * 3600 + 0 * 3600 + 0 * 60 + 0 - second_start

    for j in range(len(prediction_t)):
        ts = ts_start + t1[j] + time_deviation

        # Calculate the average angular speed
        GM = 398600500000000
        n_0 = m.sqrt(GM) / m.pow(sqrt_A, 3)
        n = n_0 + δn

        gps_week_r, gps_day_r, t_r, _ = utc_to_gps_week_seconds(ts)

        δt = a_0 + a_1 * (t_r + 604800 * (gps_week_r - gps_week) - t_oc) + a_2 * (
                t_r + 604800 * (gps_week_r - gps_week) - t_oc) ** 2
        t_r = t_r - δt - t_oc + 604800 * (gps_week_r - gps_week)
        t_k = t_r

        # Calculate the mean anomaly
        M_k = M0 + n * t_k
        E = 0
        E1 = 1
        count = 0
        while abs(E1 - E) > 1e-10:
            count = count + 1
            E1 = E
            E = M_k + e * m.sin(E)
            if count > 1e8:
                print("No convergence")
                break

        # Calculate the true anomaly
        V_k = m.atan2((m.sqrt(1 - e * e) * m.sin(E)), (m.cos(E) - e))

        # Calculate the right ascension of the ascending node
        u_0 = V_k + w

        # Perturbation correction
        δu = C_uc * m.cos(2 * u_0) + C_us * m.sin(2 * u_0)
        δr = C_rc * m.cos(2 * u_0) + C_rs * m.sin(2 * u_0)
        δi = C_ic * m.cos(2 * u_0) + C_is * m.sin(2 * u_0)

        u = u_0 + δu
        r = m.pow(sqrt_A, 2) * (1 - e * m.cos(E)) + δr
        i = I_0 + δi + IDOT * t_k

        # Calculate the satellite’s coordinates in the orbital plane coordinate system
        x_k = r * m.cos(u)
        y_k = r * m.sin(u)

        omega_e = 7.292115e-5
        OMEGA_k = OMEGA + (OMEGA_DOT - omega_e) * t_k - omega_e * TEO

        # Calculate the satellite's coordinate in geocentric coordinate system
        X_k = x_k * m.cos(OMEGA_k) - y_k * m.cos(i) * m.sin(OMEGA_k)
        Y_k = x_k * m.sin(OMEGA_k) + y_k * m.cos(i) * m.cos(OMEGA_k)
        Z_k = y_k * m.sin(i)

        N, E, U, _ = XYZ2NEU(X_k, Y_k, Z_k, X0, Y0, Z0)

        AZ = atan2(E, N)
        EL = atan2(U, sqrt(E ** 2 + N ** 2))

        AZ = (-(AZ - angle_window_N)) % (2 * pi)

        if U > 0 and (-pi / 2 < AZ < pi / 2):
            AZ_set.append(AZ)
            EL_set.append(EL)
        else:
            AZ_set.append(0)
            EL_set.append(0)

    print("Prediction done: PRN " + PRN)
    return AZ_set, EL_set


def AoA_integration(interpret_path, AoA_path, location, angle_window_N):
    X0, Y0, Z0 = BLH2XYZ(location[0], location[1], location[2])
    angle_window_N = angle2rad(angle_window_N)
    constellation = ['GPS', 'BEIDOU']
    doy = time.localtime(time.time()).tm_yday
    AZ_df = pd.DataFrame()
    EL_df = pd.DataFrame()
    for i in range(len(interpret_path)):
        print("")
        print(constellation[i])
        print("")
        for file_name in os.listdir(interpret_path[i]):
            AZ_set, EL_set = satellite_prediction(interpret_path[i] + "/" + file_name, i, X0, Y0, Z0,angle_window_N)
            EL_df = pd.concat([EL_df, pd.DataFrame(EL_set)], axis=1)
            AZ_df = pd.concat([AZ_df, pd.DataFrame(AZ_set)], axis=1)
            EL_path = AoA_path + "/EL_" + str(doy) + ".csv"
            if os.path.exists(EL_path):
                os.remove(EL_path)
            AZ_path = AoA_path + "/AZ_" + str(doy) + ".csv"
            if os.path.exists(AZ_path):
                os.remove(AZ_path)

            EL_df.to_csv(EL_path, header=False)
            AZ_df.to_csv(AZ_path, header=False)
    start_time = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return start_time
