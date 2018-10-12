#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import sys

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<script src="https://code.jquery.com/jquery-3.0.0.min.js"></script>
<link href='../../data/new_stylesheet.css' rel='stylesheet' type='text/css' />
<title>観光スポット検索</title>
</head>
<body>
<header>
<h1 class='title'>観光スポット検索</h1>
</header>
<div class='left'>
<form method='post' name='form1'>
<h3 class='crowdworks_id'>ユーザ名：<input type='text' name='user_id' id='user_id' maxlength='40' style='width: 200px;height: 24px;font-size:16px;'/></h3>
<p style='text-align:center;'>行ったことがあるスポット名の入力をお願いします</p>
<h3 class='keyword'><textarea name='history_name' style='width:350px; height:150px; font-size:14px;'/></textarea></h3>
<p style='text-align:center;'>観光エリアの入力をお願いします</p>
<h3 class='keyword'>都道府県：<input type='text' name='prefecture_name' style='width:250px; height:24px; font-size:16px;'/></h3>
<h3 class='keyword'>エリア：<input type='text' name='area_name' style='width:250px; height:24px; font-size:16px;'/></h3>

<p style='color:#ff0000'><input type='radio' name='user' id='input-check' /> 全ての項目の入力し終えたら，チェックしてから「実験開始」をクリックしてください．</p>
<input type='button' class='button1' value='実験開始'/>
</form>
</div>

<div class='right'>
<h2 style='color:red;'>注意事項！！</h2>
<h3>== CrowdWorksIDについて ==</h3>
<div class='image'><img src='../../data/crowdworks_id_img.png'></div>
<h3>== 都道府県の入力に関して ==</h3>
<p style="color:red;">◯良い例：東京，大阪，京都，神奈川，北海道</p>
<p>×悪い例：東京都，大阪府，京都府，神奈川県</p>
</div>
<script>
$('.button1').click(function() {
    link= "test_02_medoid.py";
    $(this).parents('form').attr('action', link);
    $(this).parents('form').submit();
});

$(function() {
    inputCheck();
    $(':radio').change(function(){
        inputCheck();
    });
});

function inputCheck() {
    if($('#input-check').is(':checked')) {
        $('.button1').prop('disabled', false);
    } else {
        $('.button1').prop('disabled', true);
    }
}

</script>
</body>
</html>
"""
print(html_body)
