import numpy as np
import sys

def color_cyo():
    # html用rgb作成 .range(['cyan', 'yellow', 'orange']);
    num = np.arange(0, 1.01, 0.01)
    color_res = []
    r,g,b = 0,253,255
    for i in range(len(num)):
        if i < 52:
            color_res.append([num[i],"rgb(" + str(r) + ",255," + str(b) +")"])
            r = r + 5
            b = b - 5
        else:
            color_res.append([num[i],"rgb(255," + str(g) + ",0)"])
            g = g-2
    # print(color_res, file=sys.stderr)
    return color_res

def color_bor():
    ## html用rgb作成 .range(['blue', 'orange', 'red']);
    num = np.arange(0, 1.01, 0.01)
    color_res = []
    r,g,b = 0,0,255
    for i in range(len(num)):
        if i < 52:
            color_res.append([num[i],"rgb(" + str(r) + "," + str(g) + "," + str(b) +")"])
            r = r + 5
            g = g + 3
            b = b - 5
        else:
            color_res.append([num[i],"rgb(255,"+ str(g) + ",0)"])
            g = g - 3
    # print(color_res, file=sys.stderr)
    return color_res

def color_bpr():
    ## html用rgb作成 .range(['blue', 'purple', 'red']);
    num = np.arange(0, 1.01, 0.01)
    color_res = []
    r,g,b = 0,0,255
    for i in range(len(num)):
        color_res.append([num[i],"rgb(" + str(r) + "," + str(g) + "," + str(b) +")"])
        r = r + 2.5
        b = b - 2.5
    print(color_res, file=sys.stderr)
    return color_res

def color_bpr_fu():
    ## html用rgb作成 .range(['blue', 'purple', 'red']);
    num = np.arange(-1.01, 1.01, 0.01)
    color_res = []
    r,g,b = 0,0,255
    for i in range(len(num)):
        color_res.append([float(str(num[i])[:4]),"rgb(" + str(r) + "," + str(g) + "," + str(b) +")"])
        r = r + 1
        b = b - 1
    print(color_res, file=sys.stderr)
    return color_res

def color_cyo_fu():
    # html用rgb作成 .range(['cyan', 'yellow', 'orange']);
    num = np.arange(-1, 0.01, 0.01)
    color_res = []
    r,g,b = 0,253,255
    for i in range(len(num)):
        if i < 52:
            color_res.append([num[i],"rgb(" + str(r) + ",255," + str(b) +")"])
            r = r + 5
            b = b - 5
        else:
            color_res.append([num[i],"rgb(255," + str(g) + ",0)"])
            g = g-2
    # print(color_res, file=sys.stderr)
    return color_res

# def color_cbpr():
#     ## html用rgb作成 .range(['blue', 'purple', 'red']);
#     num = np.arange(-1.01, 1.01, 0.01)
#     color_res = []
#     r,g,b = 0,255,255
#     for i in range(len(num)):
#         if str(num[i])[0] == "-":
#             tmp = float(str(num[i])[:5])
#         else:
#             tmp = float(str(num[i])[:4])
#         if r == 0 and b == 255:
#             color_res.append([tmp,"rgb(0," + str(g) + ",255)"])
#         g = g - 4
#         if g == -1:
#             color_res.append([tmp,"rgb(" + str(r) + ",0," + str(b) +")"])
#             r = r + 2
#             b = b - 2
#     print(color_res, file=sys.stderr)
#     return color_res
