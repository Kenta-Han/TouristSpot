#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi,cgitb
import MySQLdb
import sys

html_body = u"""
<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<script src="https://code.jquery.com/jquery-3.0.0.min.js"></script>
<link href='../../data/stylesheet_soc2018.css' rel='stylesheet' type='text/css' />
<title>観光スポット検索</title>
</head>
<body>
<header>
<h1 class='title'>観光スポット検索</h1>
</header>
<div class='left'>
<form method='post' name='form1'>
<h3 class='crowdworks_id'>ユーザ名：<input type='text' name='user_id' id='user_id' maxlength='40' style='width: 200px;height: 24px;font-size:16px;'/></h3>
<p style='text-align:center;'>要求を3つ入力してください．</p>
<h4 class='keyword'>要求1：<input type='text' name='keyword1' style='width: 250px;height: 24px;font-size:16px;'/></h4>
<h4 class='keyword'>要求2：<input type='text' name='keyword2' style='width: 250px;height: 24px;font-size:16px;'/></h4>
<h4 class='keyword'>要求3：<input type='text' name='keyword3' style='width: 250px;height: 24px;font-size:16px;'/></h4>
<h2 class='subtitle'>== 旅行の同行者を選択してください ==</h2>
<ol class='type_choice'>
<li class='type_choice_li'><input type='radio' name='type1' value='1'>&nbsp一人</li>
<li class='type_choice_li'><input type='radio' name='type1' value='2'>&nbspカップル・夫婦</li>
<li class='type_choice_li'><input type='radio' name='type1' value='3'>&nbsp家族</li>
<li class='type_choice_li'><input type='radio' name='type1' value='4'>&nbsp友達同士</li>
<li class='type_choice_li'><input type='radio' name='type1' value='5'>&nbspその他</li>
</ol>
<h2 class='subtitle'>== 旅行に行きたい季節を選択してください ==</h2>
<ol class='type_choice'>
<li class='type_choice_li'><input type='radio' name='season1' value='1'>&nbsp春</li>
<li class='type_choice_li'><input type='radio' name='season1' value='2'>&nbsp夏</li>
<li class='type_choice_li'><input type='radio' name='season1' value='3'>&nbsp秋</li>
<li class='type_choice_li'><input type='radio' name='season1' value='4'>&nbsp冬</li>
</ol>

<p style='color:#ff0000'><input type='radio' name='user' id='input-check' /> 全ての項目の入力し終えたら，チェックしてから「実験開始」をクリックしてください．</p>
<input type='button' class='button1' value='実験開始'/>
</form>
</div>
<div class='right'>
<h2 style='color:red;'>注意事項！！</h2>
<h3>== CrowdWorksIDについて ==</h3>
<div class='image'><img src='../../data/crowdworks_id_img.png'></div>
<h3>== 要求について ==</h3>
<ol class='setumei'>
<p>悪い例</p>
<li>具体的なジャンル　<span>例：神社，公園...</span></li>
<li>具体的な場所　<span>例：東京，新宿...</span></li>
<p>良い例</p>
<li>気分，感情　<span>例：広い，のんびり，自然豊か...</span></li>
</ol>
</div>
<script>
$('.button1').click(function() {
    var a = 4; /* 6,12,18から*/
    /* a = 1 + Math.floor(Math.random()*4); */
    if(a==1){
        link= "review_only1.py";
    }
    if(a==2){
        link= "review_only1.py";
    }
    if(a==3){
        link= "review_only1.py";
    }
    if(a==4){
        link= "review_only1.py";
    }

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
