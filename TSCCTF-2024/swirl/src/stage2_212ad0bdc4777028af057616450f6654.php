<?php
include('config.php');
echo '<h1>👻 Stage 2 / 4</h1>';

$A = $_GET['A'];
$B = $_GET['B'];

highlight_file(__FILE__);
echo '<hr>';

if (isset($A) && isset($B))
    if ($A !== $B){
        $is_same = md5($A) == 0 and md5($B) === 0;
        if ($is_same)
            echo (md5($B) ? "QQ1" : md5($A) == 0 ? "<a href=$stage3?page=swirl.php>Go to stage3</a>" : "QQ2");
        else die('ERROR: $is_same is false');
    }
else die('ERROR: A, B should be given');
