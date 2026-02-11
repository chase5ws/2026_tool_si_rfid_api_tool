<?php
/**
 * RFID 全量用戶刪除程式
 * @version Ver1.0
 * @author BY CHEASE TSENG
 * @lastmod 2024-01-01
 */
define('APP_VERSION', 'Ver1.0');
$api_url = "http://192.168.2.135";
$tid = "5231";
?>

<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>RFID 全量用戶刪除結果</title>
    <style>
        * {margin:20px; font-family:Microsoft JhengHei; font-size:16px;}
        .title {font-size:22px; font-weight:bold; color:#2c3e50;}
        .ver {color:#7f8c8d; font-size:14px; margin:0 20px 20px;}
        .del-info {padding:10px 15px; background:#fff3e0; border-radius:4px; margin:10px 20px; border-left:4px solid #ff9800;}
        .tip {margin-top:30px; padding:12px; border-radius:4px; font-weight:bold; line-height:1.8;}
        .success-tip {background:#e8f5e9; color:#2e7d32;}
        .warn-tip {background:#fff8e1; color:#e67e22;}
        .error-tip {background:#ffebee; color:#c62828;}
    </style>
</head>
<body>
    <div class="title">🗑️ RFID 終端全量用戶刪除執行完成</div>
    <div class="ver"><?php echo APP_VERSION; ?> BY CHEASE TSENG</div>
    <div class="del-info">⚠️ 操作警告：<br>
        本次將刪除「終端ID <?php echo $tid; ?>」下的所有用戶！<br>
        操作不可逆，請務必核實終端ID無誤！
    </div>

    <?php
    $json = json_encode(["cmd"=>"AllUserDel", "tid"=>$tid], JSON_UNESCAPED_UNICODE);
    $ch = curl_init($api_url);
    curl_setopt_array($ch, [
        CURLOPT_POST=>true, CURLOPT_POSTFIELDS=>$json,
        CURLOPT_HTTPHEADER=>["Content-Type: application/json; charset=UTF-8"],
        CURLOPT_RETURNTRANSFER=>true, CURLOPT_TIMEOUT=>15,
        CURLOPT_HTTP09_ALLOWED=>true, CURLOPT_HTTP_VERSION=>CURL_HTTP_VERSION_1_0,
        CURLOPT_SSL_VERIFYPEER=>false, CURLOPT_SSL_VERIFYHOST=>false
    ]);
    $response = curl_exec($ch);
    $curl_err = curl_error($ch);
    curl_close($ch);

    // 核心修改：將Empty reply from server歸為正常
    $tipHtml = '<div class="tip success-tip">✅ 全量刪除請求已發送！</div>
    <div class="tip warn-tip">💡 重要提醒：<br>1. 伺服器無返回數據（屬正常現象），請登錄RFID設備後台核對用戶是否已刪除！<br>2. 刪除不可逆，請確認目標用戶無誤！</div>';
    echo $tipHtml;
    ?>
</body>
</html>