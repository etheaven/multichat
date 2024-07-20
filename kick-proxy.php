<?php
require 'vendor/autoload.php';
use KyranRana\CloudflareBypass\CFBypass;

header('Access-Control-Allow-Origin: *');
header('Content-Type: text/html; charset=utf-8');

$username = $_GET['username'] ?? '';
if (empty($username)) {
    die('Username is required');
}

$url = "https://kick.com/{$username}/chatroom";

$cfBypass = new CFBypass();
try {
    $response = $cfBypass->request($url, [
        'headers' => [
            'User-Agent' => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
    ]);

    echo $response;
} catch (Exception $e) {
    die('Error: ' . $e->getMessage());
}
