
file_path = "otherword.txt"
with open(file_path, "w") as f:
    for i in range(0,100):
        f.write(str(i) + "つ\n")
    for i in range(0,1000):
        f.write(str(i) + "個\n")
    for i in range(0,1000):
        f.write(str(i) + "番\n")
    for i in range(0,10000):
        f.write(str(i) + "人\n")
    for i in range(0,101):
        f.write(str(i) + "位\n")
    for i in range(0,101):
        f.write(str(i) + "本\n")
    for i in range(0,10000,10):
        f.write(str(i) + "円\n")
    for i in range(0,1000,10):
        f.write(str(i) + "万\n")
    for i in range(0,101):
        f.write(str(i) + "歳\n")
    for i in range(0,101):
        f.write(str(i) + "回\n")
    for i in range(1,2021):
        f.write(str(i) + "年\n")
    for i in range(-30,50):
        f.write(str(i) + "度\n")
    for i in range(1,13):
        f.write(str(i) + "月\n")
    for i in range(1,32):
        f.write(str(i) + "日\n")
    for i in range(0,25):
        f.write(str(i) + "時\n")
    for i in range(0,201):
        f.write(str(i) + "分\n")
    for i in range(0,25):
        f.write(str(i) + "年間\n")
    for i in range(0,25):
        f.write(str(i) + "年ぶり\n")
    for m in range(1,13):
        for d in range(1,32):
            f.write(str(m) + "月" + str(d) + "日\n")
    for i in range(0,101):
        f.write(str(i) + "日目\n")
    for i in range(0,25):
        f.write(str(i) + "時間\n")
    for i in range(0,25):
        f.write(str(i) + "時間前\n")
    for i in range(0,25):
        f.write(str(i) + "%\n")
    for i in range(0,100):
        f.write("No." + str(i) + "\n")

    f.write("＼/\n")
    f.write("午前\n午後\n")
    f.write("朝\n昼\n夜\n晩\n")
    f.write("ドル\n")
    f.write("の\n")
