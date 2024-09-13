import math as m
import numpy as np
import datetime
import pandas as pd

LEAP_SECONDS = 18
'''以下为三角函数调用'''
a = 6378137.0  # 参考椭球的长半轴, 单位 m
f = 1 / 298.257223563  # 参考椭球的扁率
b = 6356752.31414  # 参考椭球的短半轴, 单位 m
pi = 3.1415926
'''以下为三角函数调用'''
sqrt = m.sqrt
sin = m.sin
cos = m.cos
atan = m.atan
atan2 = m.atan2
fabs = m.fabs


def utc_to_gps_week_seconds(utc, leapseconds=LEAP_SECONDS):
    datetimeformat = "%Y-%m-%d %H:%M:%S.%f"
    utc = datetime.datetime.fromtimestamp(utc)
    epoch = datetime.datetime.strptime("1980-01-06 00:00:00.000", datetimeformat)
    tdiff = utc - epoch + datetime.timedelta(seconds=leapseconds)
    gpsweek = tdiff.days // 7
    gpsdays = tdiff.days - 7 * gpsweek
    gpsseconds = tdiff.seconds + 86400 * (tdiff.days - 7 * gpsweek)
    return gpsweek, gpsdays, gpsseconds, tdiff.microseconds


def day_of_year(date):
    return (date - datetime.date(date.year, 1, 1)).days + 1


def rx(fai):
    result = np.mat([[1, 0, 0], [0, m.cos(fai), m.sin(fai)], [0, -1 * m.sin(fai), m.cos(fai)]])
    return result


def rz(fai):
    result = np.mat([[m.cos(fai), m.sin(fai), 0], [-1 * m.sin(fai), m.cos(fai), 0], [0, 0, 1]])
    return result


def rad2angle(r):
    a = r * 180.0 / m.pi
    return a


def angle2rad(a):
    r = a * m.pi / 180.0
    return r


def BLH2XYZ(B, L, H):
    B = angle2rad(B)
    L = angle2rad(L)

    e = m.sqrt((a ** 2 - b ** 2) / (a ** 2))
    N = a / sqrt(1 - e * e * sin(B) * sin(B))

    X = (N + H) * cos(B) * cos(L)
    Y = (N + H) * cos(B) * sin(L)
    Z = (N * (1 - e * e) + H) * sin(B)
    return X, Y, Z


def xyz2blh(x, y, z):
    a = 6378137
    e2 = 0.0066943799013

    if x == 0 and y > 0:
        L = 90
    elif x == 0 and y < 0:
        L = -90
    else:
        L = m.atan2(y, x)

    t_B0 = z / m.sqrt(x * x + y * y)
    t_B1 = (a * e2 * t_B0 / m.sqrt(1 + t_B0 * t_B0 - e2 * t_B0 * t_B0) + z) / m.sqrt(x * x + y * y)

    while abs(t_B1 - t_B0) > 1e-10:
        t_B0 = t_B1
        t_B1 = (a * e2 * t_B0 / m.sqrt(1 + t_B0 * t_B0 - e2 * t_B0 * t_B0) + z) / m.sqrt(x * x + y * y)
    B = m.atan2(t_B1, 1)

    N = a / m.sqrt(1 - e2 * (m.sin(B) * m.sin(B)))
    H = m.sqrt(x * x + y * y) / m.cos(B) - N

    return B, L, H


def XYZ2NEU(X, Y, Z, X1, Y1, Z1):
    dx = X - X1
    dy = Y - Y1
    dz = Z - Z1
    B, L, H = xyz2blh(X1, Y1, Z1)
    B = angle2rad(B)
    L = angle2rad(L)
    N = -sin(B) * cos(L) * dx - sin(B) * sin(L) * dy + cos(B) * dz
    E = -sin(L) * dx + cos(L) * dy
    U = cos(B) * cos(L) * dx + cos(B) * sin(L) * dy + sin(B) * dz
    error = sqrt(pow(dx, 2) + pow(dy, 2) + pow(dz, 2))
    return N, E, U, error
