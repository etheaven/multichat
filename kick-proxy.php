<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: text/html; charset=utf-8');

$username = $_GET['username'] ?? '';
if (empty($username)) {
    die('Username is required');
}

$url = "https://kick.com/{$username}/chatroom";

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_COOKIEJAR, 'cookies.txt');
curl_setopt($ch, CURLOPT_COOKIEFILE, 'cookies.txt');
curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language: en-US,en;q=0.5',
    'Accept-Encoding: gzip, deflate, br',
    'Connection: keep-alive',
    'Upgrade-Insecure-Requests: 1'
]);

$response = curl_exec($ch);

if (curl_errno($ch)) {
    die('Curl error: ' . curl_error($ch));
}

curl_close($ch);

echo $response;
