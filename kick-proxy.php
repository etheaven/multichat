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
    'Connection: keep-alive',
    'Upgrade-Insecure-Requests: 1'
]);

$response = curl_exec($ch);

if (curl_errno($ch)) {
    die('Curl error: ' . curl_error($ch));
}

$encoding = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
curl_close($ch);

// Ensure the response is in UTF-8
if (stripos($encoding, 'charset=') === false) {
    $response = mb_convert_encoding($response, 'UTF-8', 'UTF-8, ISO-8859-1');
} elseif (stripos($encoding, 'charset=utf-8') === false) {
    $response = mb_convert_encoding($response, 'UTF-8', substr($encoding, stripos($encoding, 'charset=') + 8));
}

// Remove any BOM if present
$response = preg_replace('/^\xEF\xBB\xBF/', '', $response);

echo $response;
