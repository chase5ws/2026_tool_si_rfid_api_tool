<?php
/**
 * XAMPP Apache + PHP 測試檔案
 * 用於驗證伺服器是否正常執行，並展示環境資訊
 */

// 設定頁面編碼，避免中文亂碼
header('Content-Type: text/html; charset=utf-8');

// 頁面標題
echo "<h1>XAMPP 伺服器測試頁面</h1>";
echo "<hr>";

// 1. 基礎測試：驗證PHP是否正常執行
echo "<h3>1. PHP 執行狀態</h3>";
echo "<p>✅ PHP 指令碼執行正常！</p>";
echo "<p>目前時間：" . date('Y-m-d H:i:s') . "</p>";

// 2. 伺服器資訊
echo "<h3>2. 伺服器基本資訊</h3>";
echo "<ul>";
echo "<li>伺服器軟體：" . $_SERVER['SERVER_SOFTWARE'] . "</li>";
echo "<li>PHP 版本：" . PHP_VERSION . "</li>";
echo "<li>伺服器IP：" . $_SERVER['SERVER_ADDR'] . "</li>";
echo "<li>存取連接埠：" . $_SERVER['SERVER_PORT'] . "</li>";
echo "</ul>";

// 3. 可選：展示完整的PHP配置資訊（取消下面註解可查看）
// echo "<h3>3. 完整PHP配置資訊</h3>";
// phpinfo();

echo "<hr>";
echo "<p style='color: green; font-weight: bold;'>如果能看到以上內容，代表你的 XAMPP Apache 伺服器和 PHP 環境都已正常執行！</p>";
?>