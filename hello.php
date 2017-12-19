<html>
<head>
<title>Скрипт python</title>
</head>
<body>
<?php echo '<p>Выполнение скрипта python</p>'; ?>

<form enctype="multipart/form-data" action="hello.php" method="post">
<input type="hidden" name="MAX_FILE_SIZE" value="30000">
Отправить файл: <input name="userfile" type="file">
<input type="submit" value="Отправить">
</form>

<?php
$uploaddir = '/var/www/html/uploads/';
if (move_uploaded_file($_FILES['userfile']['tmp_name'], $uploaddir . 
	$_FILES['userfile']['name'])) {
	$file = $_FILES['userfile']['name'];
    print "Файл успешно загружен";
} else {
    print "Повторите попытку!";
}

?>

<?php
//$name = 'filetest.txt';
print $file;
$ch = curl_init("http://localhost:8082/?". $file);
$fp = fopen("/home/koval/Загрузки/text.txt", "rw");

curl_setopt($ch, CURLOPT_FILE, $fp);
curl_setopt($ch, CURLOPT_HEADER, 0);

curl_exec($ch);
curl_close($ch);
fclose($fp);

$filename="/home/koval/Загрузки/text.txt";
$fd=fopen($filename, "r");
$contents=fread($fd, filesize ($filename));

$contents=str_replace("\r\n","<br>",$contents);

fclose ($fd);
print $contents;

?>
</body>
</html>
