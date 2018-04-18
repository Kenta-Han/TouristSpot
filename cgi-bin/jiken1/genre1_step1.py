#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<script src="https://code.jquery.com/jquery-3.0.0.min.js"></script>
<link href='/data/stylesheet_onlytype.css' rel='stylesheet' type='text/css' />
<title>ジャンル選択</title>

<script>
$(function() {
    $('.button1').click(
    function() {
        $.ajax({
          url: 'genre1_step2.py',
          type: 'POST',
          data:{
            'genre':$("input[name='genre']:checked").val() /* only_type2_1.pyにgenreを送信 */
          },
          dataType: 'html',
          success: function(data) {
            $('#text').html(data);
          },
          error: function(data) {
            alert('既に選択しています');
          }
        });
    }
    );
});
</script>
</head>

<body>
<header><h1 style='text-align:center;'>観光スポット検索(B)</h1></header>

<table class='imagetable'>
<tr>
<th colspan=4><h2>　ジャンルを選んでください　</h2></th>
</tr>
<tr>
<td><input type='radio' name='genre' value='1'>&nbspアウトドア</td>
<td><input type='radio' name='genre' value='2'>&nbspウォータースポーツ・マリンスポーツ</td>
<td><input type='radio' name='genre' value='3'>&nbsp雪・スノースポーツ</td>
</tr>
<tr>
<td><input type='radio' name='genre' value='4'>&nbspその他スポーツ・フィットネス</td>
<td><input type='radio' name='genre' value='5'>&nbspエンタメ・アミューズメント</td>
<td><input type='radio' name='genre' value='6'>&nbspレジャー・体験</td>
</tr>
<tr>
<td><input type='radio' name='genre' value='7'>&nbspクラフト・工芸</td>
<td><input type='radio' name='genre' value='8'>&nbsp果物・野菜狩り</td>
<td><input type='radio' name='genre' value='9'>&nbspミュージアム・ギャラリー</td>
</tr>
<tr>
<td><input type='radio' name='genre' value='10'>&nbsp神社・神宮・寺院</td>
<td><input type='radio' name='genre' value='11'>&nbsp伝統文化・日本文化</td>
<td><input type='radio' name='genre' value='12'>&nbsp自然景観・絶景</td>
</tr>
<tr>
<td><input type='radio' name='genre' value='13'>&nbsp乗り物</td>
<td><input type='radio' name='genre' value='14'>&nbsp動・植物</td>
<td><input type='radio' name='genre' value='15'>&nbsp風呂・スパ・サロン</td>
</tr>
<tr>
<td><input type='radio' name='genre' value='16'>&nbspショッピング</td>
<td><input type='radio' name='genre' value='17'>&nbsp観光施設・名所巡り</td>
<td><input type='radio' name='genre' value='18'>&nbsp祭り・イベント</td>
</tr>
</table>
<input type='button' class='button1' value='選択'/>

<div id='text'></div>

</body>
</html>
"""

print(html_body)
