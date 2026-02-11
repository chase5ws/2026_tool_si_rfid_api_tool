
<?php

// Values to insert
$Equipld  = "FAB11B-PACK108";
$Position = "Null";
$tid      = "5231";
$cardtimeout = "60";
$rfidtimeout = "20";
$url = "192.168.2.135";


// Build JSON data
$data = array(
    "cmd"      		=> "setcfg",
	"Equipld"     	=> $Equipld,
	"Position"    	=> $Position,
    "tid"      		=> $tid,
    "cardtimeout"   => $cardtimeout,
    "rfidtimeout" 	=> $rfidtimeout,
    "url"   		=> $url
);

$jsonData = json_encode($data);

// API URL (your IPC IP)
$url = "192.168.2.135";

// Initialize cURL
$ch = curl_init($url);

// cURL options
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);
curl_setopt($ch, CURLOPT_HTTPHEADER, array(
    'Content-Type: application/json',
    'Content-Length: ' . strlen($jsonData)
));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

// Execute request
$response = curl_exec($ch);

// Check errors
if ($response === false) {
    echo "cURL Error: " . curl_error($ch);
} else {
    echo "Response: " . $response;
}

curl_close($ch);
