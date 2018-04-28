#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb

print("<!DOCTYPE html>")
print("<head>")
print("Content-type:text/html; charset=UTF-8\r\n")
print("<meta http-equiv='content-type' content='text/html; />")
print("<script src='https://code.jquery.com/jquery-3.0.0.min.js'></script>")
print("<link href='../../data/stylesheet_onlytype.css' rel='stylesheet' type='text/css' />")
print("<title>ジャンル選択2</title>")
print("</head>")

print("<body>")
category01 = ["バーベキュー","パラグライダー","モーターパラグライダー","ハンググライダー","トレッキング・登山","ウォーキング・ハイキング","ジップライン","洞窟体験・ケイビング","フォレストアドベンチャー","キャンプ場","バードウォッチング","ツリークライミング","アスレチック","野外レクリエーション","ナイトツアー","スカイダイビング","バンジージャンプ","オリエンテーリング・パーマネントコース","その他アウトドア"]

category02 = ["スキューバダイビング","シュノーケリング・ボートシュノーケル","カヌー・カヤック","マングローブカヤック・カヌー","ラフティング","パラセーリング","川下り・ライン下り","SUP・スタンドアップパドル","キャニオニング","ホバーボード・フライボード","バナナボート・チュービング","シャワークライミング","ウォーターボール","サーフィン・ボディボード","ウェイクボード・ウェイクサーフィン","ウィンドサーフィン","カイトサーフィン","リバーブギ・ハイドロスピード","水上バイク","シーウォーカー","川遊び・水辺遊び","ウォータージャンプ","プール","素潜り・スキンダイビング","ヨット・ヨットセーリング","その他ウォータースポーツ・マリンスポーツ"]

category03 = ["わかさぎ釣り","スノーシュー・スノートレッキング","スキー場・スノーボードゲレンデ","その他雪・スノースポーツ","エアボード","テレマークスキー","クロスカントリースキー","アイススケート場","犬ぞり","スノーモービル"]

category04 = ["乗馬","ボルダリング・ロッククライミング","バギー","アーチェリー","マウンテンバイク","サイクリング","ゴルフ・ゴルフ場","モトクロス","スポーツリゾート施設","サッカー","バブルサッカー","フットサル","スポーツ観戦","その他スポーツ・フィットネス"]

category05 = ["脱出ゲーム","宝探し（トレジャーハント）","フライトシミュレーター","サバゲー(サバイバルゲーム)","ディナーショー","ダンス","テーマパーク・レジャーランド","カラオケ・パーティ","インターネットカフェ・マンガ喫茶","その他エンタメ・アミューズメント"]

category06 = ["バイキング・ビュッフェ・ホテルレストラン","仕事体験（職業体験）","イルカウォッチング・イルカスイム","ホエールウォッチング","うどん・そば打ち","釣り","離島ツアー","自然体験","着付け体験","梅干し作り","お菓子作り","グラスボート","食品サンプル製作","ピザ作り","熱気球","牧場・酪農体験","動物ふれあい体験","ワイン作り","舞妓体験","ソーセージ・ウィンナー作り","民謡ライブ","茶道","機織り","野生動物観察","体験観光","日本酒作り・醸造体験","塩作り","忍者・侍・武士体験","収穫","三味線体験","ジャム作り","農業体験","おやき作り","工場見学","昆虫採集","トールペイント","無人島ツアー","漁業体験・潮干狩り・地引網","楽器作り","味噌作り","化石発掘","こけし絵付け","調香","バウムクーヘン作り","琉球舞踊体験","3Dプリンター体験","林業体験","ガーデニング","レジャースポット","花摘み・ハーブ摘み","家具作り","生け花・華道","禅・座禅","田舎暮らし体験","武道･武術体験","ドッグラン","写真体験","その他レジャー・体験"]

category07 = ["陶芸体験","ガラス細工作り","アクセサリー作り","ものづくり","キャンドル作り","染色・染物体験","藍染め体験","草木染め","フラワーアレンジメント","ポーセラーツ・ポーセリンアート","レザークラフト","ランプシェード作り","織物","箸作り","木工","手作りオルゴール","香水作り","紙漉き","絵画・版画体験","石鹸作り","彫金体験","靴作り","人形作り","苔玉作り","マリンクラフト","スペインタイル","クリスマスリース作り","押し花体験","時計作り","竹細工作り","フィギュア制作","エアブラシ塗装体験","グルーデコ","クレイアート","メガネ作り","江戸切子","竹炭・花炭作り","彫紙アート","カルトナージュ","シュガークラフト","漆工芸","布草履作り","カービング","パッチワーク","扇子絵付け体験","彫刻","焼き絵","その他クラフト・工芸"]

category08 = ["いちご狩り","みかん狩り","ぶどう狩り","キノコ採り","りんご狩り","その他果物・野菜狩り","桃狩り","ブルーベリー狩り","梨狩り","芋掘り","さくらんぼ狩り","トマト狩り","プラム狩り"]

category09 = ["映画ワークショップ","写真館","資料館","科学館","その他ミュージアム・ギャラリー","美術館","文化施設","社会見学・社会科見学","プラネタリウム","博物館"]

category10 = ["寺院・寺社巡り","神社・神宮巡り","その他神社・神宮・寺院"]

category11 = ["伝統工芸","郷土芸能・伝統芸能","日本文化","伝統舞踊","その他伝統文化"]

catgeory12 = ["海岸景観","郷土景観","湖沼","高原","山岳","施設景観","運河・河川景観","自然歩道・自然研究路","湿原","夜景スポット","その他自然景観・絶景","ビーチ・海水浴場","滝・渓谷","自然現象"]

category13 = ["クルージング","屋形船・納涼船","人力車","セグウェイ","レンタサイクル","レンタカー","原付・バイクレンタル","リムジンレンタル","ゴーカート・公道カート","ケーブルカー・ロープウェイ","レールバイク","ヘリコプター遊覧","セスナ・遊覧飛行","観光馬車","観光バス・タクシー・ハイヤー","その他乗り物"]

category14 = ["植物","その他動・植物","動物"]

category15 = ["貸切温泉・貸切露天・貸切風呂","エステ","リラクゼーション","岩盤浴","その他美容施設","健康ランド・スーパー銭湯","その他風呂・スパ・サロン","日帰り温泉","貸切風呂・貸切露天"]

category16 = ["アウトレットモール","ショッピングセンター","その他ショッピング","特産物（味覚）","名産品","センター施設"]

category17 = ["観光コース","町めぐり","神社・神宮巡り(廃止)","史跡・名所巡り","酒造巡り","お城巡り","寺院・寺社巡り(廃止)","牧場・酪農","動物園・植物園","マリーナ・ヨットハーバー","公園・庭園","文化史跡・遺跡","その他観光施設","地域風俗・風習","城郭","展望台・展望施設","旧街道","歴史的建造物","水族館","海中公園","産業観光施設","町並み","観光ボランティア","観光案内所","近代建築","道の駅・サービスエリア","教会・モスク","ダム"]

category18 = ["イベント","花火大会","祭り","その他祭り・イベント"]

form = cgi.FieldStorage()
category_id = int(form.getvalue('genre1')) ## only_type1_1.pyのgenre1を受け取る

cnt_category_alone = 1

print("<form method='post' action='only_type1_3.py'>")
## only_type1_3.pyにgenre2を送信
print("<input type='hidden' name='genre1' value='"+str(category_id)+"'>")

print("<table class='imagetable'>")
print("<tr><th colspan=4><h2>　ジャンルを選んでください2　</h2></th></tr>")
if category_id == 1:
    for i in category01 :
        print("<tr><td><input type='radio' name='genre2' value='"+category01[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 2:
    for i in category02 :
        print("<tr><td><input type='radio' name='genre2' value='"+category02[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 3:
    for i in category03 :
        print("<tr><td><input type='radio' name='genre2' value='"+category03[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 4:
    for i in category04 :
        print("<tr><td><input type='radio' name='genre2' value='"+category04[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 5:
    for i in category05 :
        print("<tr><td><input type='radio' name='genre2' value='"+category05[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 6:
    for i in category06 :
        print("<tr><td><input type='radio' name='genre2' value='"+category06[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 7:
    for i in category07 :
        print("<tr><td><input type='radio' name='genre2' value='"+category07[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 8:
    for i in category08 :
        print("<tr><td><input type='radio' name='genre2' value='"+category08[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 9:
    for i in category09 :
        print("<tr><td><input type='radio' name='genre2' value='"+category09[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 10:
    for i in category10 :
        print("<tr><td><input type='radio' name='genre2' value='"+category10[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 11:
    for i in category11 :
        print("<tr><td><input type='radio' name='genre2' value='"+category11[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 12:
    for i in category12 :
        print("<tr><td><input type='radio' name='genre2' value='"+category12[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 13:
    for i in category13 :
        print("<tr><td><input type='radio' name='genre2' value='"+category13[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 14:
    for i in category14 :
        print("<tr><td><input type='radio' name='genre2' value='"+category14[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 15:
    for i in category15 :
        print("<tr><td><input type='radio' name='genre2' value='"+category15[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 16:
    for i in category16 :
        print("<tr><td><input type='radio' name='genre2' value='"+category16[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 17:
    for i in category17 :
        print("<tr><td><input type='radio' name='genre2' value='"+category17[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1
elif category_id == 18:
    for i in category18 :
        print("<tr><td><input type='radio' name='genre2' value='"+category18[cnt_category_alone-1]+"'>&nbsp")
        print(i)
        print("</td></tr>")
        cnt_category_alone += 1

print("</table>")
print("<input type='submit' class='button1' value='送信'/>")
print("</form>")

print("</body></html>")
