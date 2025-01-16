<?php
include('config.php');
echo '<h1>👻 Stage 1 / 4</h1>';

$A = $_GET['A'];
$B = $_GET['B'];

highlight_file(__FILE__);
echo '<hr>';

if (isset($A) && isset($B))
    if ($A != $B)
        if (strcmp($A, $B) == 0)
            if (md5($A) === md5($B))
                echo "<a href=$stage2>Go to stage2</a>";
            else die('ERROR: MD5(A) != MD5(B)');
        else die('ERROR: strcmp(A, B) != 0');
    else die('ERROR: A == B');
else die('ERROR: A, B should be given');
