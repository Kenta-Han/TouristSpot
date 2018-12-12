## deletewordを作成するため


a = ["あ","い","う","え","お","か","き","く","け","こ","さ","し","す","せ","そ","た","ち","つ","て","と","な","に","ぬ","ね","の","は","ひ","ふ","へ","ほ","ま","み","む","め","も","や","ゆ","よ","ら","り","る","れ","ろ","わ","を","ん"]

all = []
for i in range(len(a)):
    for j in range(len(a)):
        all.append(a[i]+a[j])
# print(all)

file_path = "deleteword.txt"
with open(file_path, "w") as f:
    for i in all:
        f.write(i + "\n")
