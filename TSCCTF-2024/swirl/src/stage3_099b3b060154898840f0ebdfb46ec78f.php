<?php
include('config.php');
echo '<h1>👻 Stage 3 / 4</h1>';

$page = $_GET['page'];

highlight_file(__FILE__);
echo '<hr>';
if (isset($page)) {
    $path = strtolower($_GET['page']);
    
    // filter \ _ /
    if (preg_match("/\\_|\//", $path)) {
        echo "<p>bad hecker detect! </p>";
    }else{
        $path = str_replace("..\\", "../", $path);
        $path = str_replace("..", ".", $path);
        echo $path;
        echo '<hr>';
        echo file_get_contents("./page/".$path);
    }
} else die('ERROR: page should be given');

