<?php
/**
 * RFID 用戶循環註冊 - Ver1.0 和儀訂製版本 BY CHEASE TSENG
 * 兼容PHP7.0+ | 無回傳不報錯 | 姓名超限強制提交 | 單筆1秒間隔
 */
// 配置區（僅需修改這裡）
$api_url = "http://192.168.2.135"; // 必須加http://，有端口補：如http://192.168.2.135:8080
$default_tid = "5231";             // 默認TID
$request_delay = 1;                // 固定單筆請求間隔（秒）
// 註冊列表（無需修正姓名長度，強制提交）
$user_list = [
    ["userid" => "2", "username" => "漩渦鳴", "cardno" => "1000009"],
    ["userid" => "3", "username" => "宇智波佐助", "cardno" => "1000002"],
    ["userid" => "5", "username" => "旗木卡卡西", "cardno" => "1000004"],
    ["userid" => "6", "username" => "海野伊魯卡", "cardno" => "1000005"],
    ["userid" => "7", "username" => "奈良鹿丸", "cardno" => "1000006"],
    ["userid" => "8", "username" => "山中井野", "cardno" => "1000007"],
    ["userid" => "10", "username" => "日向寧次", "cardno" => "1000099"],
    ["userid" => "11", "username" => "李洛克", "cardno" => "1000010"],
    ["userid" => "12", "username" => "天天", "cardno" => "1000011"],
    ["userid" => "13", "username" => "日向雛田", "cardno" => "1000012"],
    ["userid" => "14", "username" => "犬塚牙", "cardno" => "1000099"],
    ["userid" => "15", "username" => "油女志乃", "cardno" => "1000014"],
    ["userid" => "16", "username" => "春野櫻", "cardno" => "1000015"],
    ["userid" => "17", "username" => "宇智波鼬", "cardno" => "1000016"],
    ["userid" => "18", "username" => "幹柿鬼鮫", "cardno" => "1000017"],
    ["userid" => "22", "username" => "test", "cardno" => "1234567"],
    ["userid" => "23", "username" => "ddd", "cardno" => "1234568"],
];

// 調試開關（正式環境保持false，不顯示任何調試訊息）
$debug_mode = false;
?>
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>RFID用戶註冊</title>
    <style>
        * {margin:20px; font-family:Microsoft JhengHei; font-size:16px;}
        .title {font-size:22px; font-weight:bold; color:#2c3e50;}
        .user-item {padding:8px 15px; background:#f8f9fa; border-radius:4px; margin:10px 20px;}
        .tip {margin-top:30px; padding:12px; background:#fff8e1; border-radius:4px; color:#e67e22; font-weight:bold;}
        .ver {color:#7f8c8d; font-size:14px; margin:0 20px 15px;}
        .debug {margin:10px 20px; padding:8px; background:#f1f1f1; border-radius:4px; font-size:14px; color:#34495e;}
    </style>
</head>
<body>
    <div class="title">📋 RFID用戶註冊執行完成</div>
    <div class="ver">Ver1.0 和儀訂製版本 BY CHEASE TSENG</div>
    <div>本次註冊帳號（單筆間隔1秒發送）：</div>

    <?php
    // 循環逐筆發送請求：兼容低版本PHP + 無任何錯誤提示 + 強制提交所有用戶
    foreach ($user_list as $k => $u) {
        // 1. 構建JSON請求（無姓名驗證，直接提交）
        $json = json_encode(
            array(
                "cmd"      => "register",
                "tid"      => $default_tid,
                "userid"   => $u['userid'],
                "username" => $u['username'],
                "cardno"   => $u['cardno'],
                "status"   => "1",
                "time"     => "0"
            ),
            JSON_UNESCAPED_UNICODE
        );

        // 2. 初始化cURL（适配無回傳伺服器，低版本PHP兼容配置）
        $ch = curl_init($api_url);
        curl_setopt_array($ch, array(
            CURLOPT_POST           => true,
            CURLOPT_POSTFIELDS     => $json,
            CURLOPT_HTTPHEADER     => array("Content-Type: application/json; charset=UTF-8"),
            CURLOPT_RETURNTRANSFER => false, // 關閉返回值接收，适配無回傳
            CURLOPT_TIMEOUT        => 5,     // 縮短超時，節省資源
            CURLOPT_SSL_VERIFYPEER => false,
            CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_FAILONERROR    => false  // 禁止無回傳拋錯，保證循環繼續
        ));

        // 3. 執行請求，不捕獲任何回傳/錯誤（解決Empty reply from server報錯）
        curl_exec($ch);
        curl_close($ch); // 立即釋放資源，避免佔用

        // 4. 頁面僅展示純淨用戶信息，無任何錯誤提示【核心語法錯誤修正處】
        echo '<div class="user-item">'.($k+1).'. 用戶ID：'.$u['userid'].' | 姓名：'.$u['username'].' | 卡號：'.$u['cardno'].'</div>';
        
        // 調試訊息（僅測試時開啟，低版本PHP兼容）
        if ($debug_mode) {
            $ch_debug = curl_init($api_url);
            curl_setopt_array($ch_debug, array(CURLOPT_RETURNTRANSFER=>true, CURLOPT_TIMEOUT=>5));
            curl_exec($ch_debug);
            $debug_error = curl_error($ch_debug);
            curl_close($ch_debug);
            // 替換??為低版本兼容的三元運算符
            $debug_msg = $debug_error ? $debug_error : '無異常';
            echo "<div class='debug'>📝 調試 - 請求JSON：{$json}<br>🌐 地址：{$api_url}<br>ℹ️ 訊息：{$debug_msg}</div>";
        }

        // 5. 核心：每筆請求後強制延遲1秒，包括最後一筆
        sleep($request_delay);
    }
    ?>

    <!-- 唯一核心提醒：僅後台確認 -->
    <div class="tip">💡 重要提醒：請登錄RFID設備後台，核對用戶是否註冊成功！</div>
</body>
</html>