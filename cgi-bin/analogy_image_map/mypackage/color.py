import numpy as np

def Color_CYO():
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

def Color_BOR():
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

def Color_BPR():
    ## html用rgb作成 .range(['blue', 'purple', 'red']);
    num = np.arange(0, 1.01, 0.01)
    color_res = []
    r,g,b = 0,0,255
    for i in range(len(num)):
        color_res.append([num[i],"rgb(" + str(r) + "," + str(g) + "," + str(b) +")"])
        r = r + 3
        b = b - 3
    # print(color_res, file=sys.stderr)
    return color_res
