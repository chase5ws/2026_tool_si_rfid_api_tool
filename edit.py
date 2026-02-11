import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import pandas as pd
import re
import socket  # 用於檢查端口占用

# 配置檔案路徑
CONFIG_FILE = "rfid_tool.setting.txt"
# PHP文件路徑配置 - 新增rfid_set_cfg.php
PHP_SET_CFG_FILE = "rfid_set_cfg.php"
PHP_DELETE_FILE = "rfid_del_user.php"
PHP_ALL_DELETE_FILE = "rfid_all_del_user.php"
PHP_REGISTER_FILE = "rfid_register_user.php"
# URL配置
DELETE_URL = "http://localhost/rfid_tool/rfid_del_user.php"
ALL_DELETE_URL = "http://localhost/rfid_tool/rfid_all_del_user.php"
REGISTER_URL = "http://localhost/rfid_tool/rfid_register_user.php"
TEST_URL = "http://localhost/rfid_tool/test.php"
# Apache默認端口
APACHE_DEFAULT_PORT = 80

class RFIDUploadTool:
    def __init__(self, root):
        self.root = root
        self.root.title("RFID 後台上傳工具 客製版 By:ChaseTseng")
        self.root.geometry("800x550")
        
        # 初始化配置變數
        self.ipc_part1 = tk.StringVar()
        self.ipc_part2 = tk.StringVar()
        self.ipc_part3 = tk.StringVar()
        self.ipc_part4 = tk.StringVar()
        self.xampp_var = tk.StringVar()
        self.user_list_var = tk.StringVar()
        self.tid_var = tk.StringVar(value="5231")  # 終端TID配置-後台保留，不顯示
        
        # 存儲讀取的Excel數據
        self.excel_data = None
        self.current_selected_item = None  # 記錄當前選中的表格行
        
        # 顯示第一步界面
        self.show_step1()
    

    def load_config(self):
        """載入rfid_tool.setting.txt中的配置，拆分IPC為四段，加載TID（後台）"""
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                f.write('IPC=""\nxampp=""\nuser_list=""\nTID="5231"\n')
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                ipc_full = ""
                for line in lines:
                    line = line.strip()
                    if line.startswith("IPC="):
                        ipc_full = line.split('"')[1]
                    elif line.startswith("xampp="):
                        self.xampp_var.set(line.split('"')[1])
                    elif line.startswith("user_list="):
                        self.user_list_var.set(line.split('"')[1])
                    elif line.startswith("TID="):
                        self.tid_var.set(line.split('"')[1])  # 後台加載TID，不顯示
            
            if ipc_full and "." in ipc_full:
                ipc_parts = ipc_full.split(".")
                self.ipc_part1.set(ipc_parts[0] if len(ipc_parts)>=1 else "")
                self.ipc_part2.set(ipc_parts[1] if len(ipc_parts)>=2 else "")
                self.ipc_part3.set(ipc_parts[2] if len(ipc_parts)>=3 else "")
                self.ipc_part4.set(ipc_parts[3] if len(ipc_parts)>=4 else "")
        except Exception as e:
            messagebox.showerror("錯誤", f"讀取配置檔案失敗：{str(e)}")
    
    def update_rfid_set_cfg_php(self):
        """Step1核心新增：更新rfid_set_cfg.php中的$url為配置的IPC IP"""
        ipc_full = self.get_full_ipc()
        if not ipc_full:
            messagebox.warning("警告", "IPC IP配置不正確，無法更新rfid_set_cfg.php！")
            return False
        
        # 檢查rfid_set_cfg.php文件是否存在
        if not os.path.exists(PHP_SET_CFG_FILE):
            messagebox.showerror("錯誤", f"找不到文件：{PHP_SET_CFG_FILE}，請確認文件在當前路徑！")
            return False
        
        try:
            # 讀取PHP文件內容
            with open(PHP_SET_CFG_FILE, 'r', encoding='utf-8') as f:
                php_content = f.read()
            
            # 正則替換$url = "原IP"; 為配置的IPC IP（兼容前後空格、引號格式）
            # 匹配規則：$url 後可跟任意空格，= 前後可跟任意空格，值為引號包裹的任意內容
            php_content = re.sub(
                r'\$url\s*=\s*"[^"]+";',
                f'$url = "{ipc_full}";',
                php_content
            )
            
            # 寫回修改後的內容
            with open(PHP_SET_CFG_FILE, 'w', encoding='utf-8') as f:
                f.write(php_content)
            
            return True
        except Exception as e:
            messagebox.showerror("錯誤", f"更新rfid_set_cfg.php失敗：{str(e)}")
            return False
    
    def get_full_ipc(self):
        """拼接4個輸入框的內容為完整IP位置"""
        part1 = self.ipc_part1.get().strip()
        part2 = self.ipc_part2.get().strip()
        part3 = self.ipc_part3.get().strip()
        part4 = self.ipc_part4.get().strip()
        
        # 驗證IP段合法性
        for part in [part1, part2, part3, part4]:
            if part:
                if not part.isdigit():
                    messagebox.warning("警告", "IP段必須為數字！")
                    return ""
                if int(part) < 0 or int(part) > 255:
                    messagebox.warning("警告", "IP段數值必須在0-255之間！")
                    return ""
        
        return f"{part1}.{part2}.{part3}.{part4}"
    
    def save_config(self):
        """保存配置到rfid_tool.setting.txt，自動拼接IPC，保存TID（後台）"""
        ipc_full = self.get_full_ipc()
        if not ipc_full and (self.ipc_part1.get() or self.ipc_part2.get() or self.ipc_part3.get() or self.ipc_part4.get()):
            return False
        
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                f.write(f'IPC="{ipc_full}"\n')
                f.write(f'xampp="{self.xampp_var.get()}"\n')
                f.write(f'user_list="{self.user_list_var.get()}"\n')
                f.write(f'TID="{self.tid_var.get()}"\n')  # 後台保存TID，不顯示
            return True
        except Exception as e:
            messagebox.showerror("錯誤", f"保存配置失敗：{str(e)}")
            return False
    
    def select_xampp_path(self):
        """選擇xampp資料夾路徑"""
        folder_path = filedialog.askdirectory(title="選擇XAMPP資料夾位置")
        if folder_path:
            self.xampp_var.set(folder_path)
    
    def select_user_list_file(self):
        """選擇user_list.xlsx檔案"""
        file_path = filedialog.askopenfilename(
            title="選擇user_list.xlsx檔案",
            filetypes=[("Excel檔案", "*.xlsx"), ("所有檔案", "*.*")]
        )
        if file_path:
            self.user_list_var.set(file_path)
    
    def show_step1(self):
        """顯示第一步：確認檔案位置界面（移除TID顯示，新增更新rfid_set_cfg.php邏輯）"""
        # 清空當前界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 標題欄
        title_label = ttk.Label(self.root, text="Step1:確認檔案位置", font=("Arial", 14, "bold"))
        title_label.pack(pady=15)
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(0, weight=0)
        
        # 1. IPC配置行（保留，核心用於更新rfid_set_cfg.php）
        ttk.Label(main_frame, text="IPC IP位置：").grid(row=0, column=0, sticky=tk.W, pady=10, padx=(0, 5))
        ip_frame = ttk.Frame(main_frame)
        ip_frame.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        ip1_entry = ttk.Entry(ip_frame, textvariable=self.ipc_part1, width=5)
        ip1_entry.pack(side=tk.LEFT, padx=(0, 1))
        ttk.Label(ip_frame, text=".").pack(side=tk.LEFT, padx=(0, 1))
        ip2_entry = ttk.Entry(ip_frame, textvariable=self.ipc_part2, width=5)
        ip2_entry.pack(side=tk.LEFT, padx=(0, 1))
        ttk.Label(ip_frame, text=".").pack(side=tk.LEFT, padx=(0, 1))
        ip3_entry = ttk.Entry(ip_frame, textvariable=self.ipc_part3, width=5)
        ip3_entry.pack(side=tk.LEFT, padx=(0, 1))
        ttk.Label(ip_frame, text=".").pack(side=tk.LEFT, padx=(0, 1))
        ip4_entry = ttk.Entry(ip_frame, textvariable=self.ipc_part4, width=5)
        ip4_entry.pack(side=tk.LEFT)
        
        # 移除原TID配置行，不顯示給用戶，後台保留配置
        
        # 2. XAMPP路徑配置行（保留）
        ttk.Label(main_frame, text="XAMPP路徑：").grid(row=1, column=0, sticky=tk.W, pady=10, padx=(0, 5))
        xampp_entry = ttk.Entry(main_frame, textvariable=self.xampp_var, width=50)
        xampp_entry.grid(row=1, column=1, padx=(0, 10), pady=10, sticky=tk.W)
        xampp_btn = ttk.Button(main_frame, text="選擇資料夾", command=self.select_xampp_path)
        xampp_btn.grid(row=1, column=2, pady=10)
        
        # 3. User_list檔案配置行（保留）
        ttk.Label(main_frame, text="User_List檔案：").grid(row=2, column=0, sticky=tk.W, pady=10, padx=(0, 5))
        user_list_entry = ttk.Entry(main_frame, textvariable=self.user_list_var, width=50)
        user_list_entry.grid(row=2, column=1, padx=(0, 10), pady=10, sticky=tk.W)
        user_list_btn = ttk.Button(main_frame, text="選擇檔案", command=self.select_user_list_file)
        user_list_btn.grid(row=2, column=2, pady=10)
        
        # 保存並更新按鈕（合併：保存配置 + 更新rfid_set_cfg.php）
        save_update_btn = ttk.Button(
            main_frame, 
            text="保存配置並更新IP配置", 
            command=self.save_config_and_update_php,
            style="Accent.TButton"
        )
        save_update_btn.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        # 下一步按鈕（置底）
        next_btn = ttk.Button(self.root, text="下一步", command=self.go_to_step2, style="Accent.TButton")
        next_btn.pack(side=tk.BOTTOM, pady=20)
        
        # 載入配置
        self.load_config()
    
    def save_config_and_update_php(self):
        """合併操作：先保存配置，再更新rfid_set_cfg.php的IP"""
        # 第一步：保存本地配置
        if not self.save_config():
            return
        messagebox.showinfo("成功", "本地配置已保存！")
        
        # 第二步：更新rfid_set_cfg.php
        if self.update_rfid_set_cfg_php():
            messagebox.showinfo("成功", f"已成功更新{PHP_SET_CFG_FILE}的IPC IP配置！")
    
    def go_to_step2(self):
        """進入第二步：讀取Excel數據（先校驗配置和PHP文件更新狀態）"""
        # 先校驗IPC配置是否有效（用於rfid_set_cfg.php）
        ipc_full = self.get_full_ipc()
        if not ipc_full:
            messagebox.warning("警告", "請先配置有效的IPC IP並保存！")
            return
        
        # 校驗rfid_set_cfg.php是否存在（非強制，僅提示）
        if not os.path.exists(PHP_SET_CFG_FILE):
            if not messagebox.askyesno("提示", f"未找到{PHP_SET_CFG_FILE}，是否繼續？", parent=self.root):
                return
        
        # 檢查user_list文件是否選擇
        user_list_path = self.user_list_var.get()
        if not user_list_path or not os.path.exists(user_list_path):
            messagebox.warning("警告", "請先選擇有效的User_List檔案！")
            return
        
        # 讀取Excel文件
        try:
            # 讀取Excel，只保留指定列
            df = pd.read_excel(user_list_path)
            # 確保列名正確（忽略大小寫和多餘空格）
            df.columns = df.columns.str.strip().str.lower()
            required_cols = ['userid', 'username', 'cardno']
            
            # 檢查必要列是否存在
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                messagebox.warning("警告", f"Excel檔案缺少必要列：{', '.join(missing_cols)}")
                return
            
            # 只保留需要的列並存儲（填充空值為空字串，統一轉為字串類型避免類型錯誤）
            self.excel_data = df[required_cols].copy().fillna("").astype(str)
            # 顯示第二步界面
            self.show_step2()
        except Exception as e:
            messagebox.showerror("錯誤", f"讀取Excel檔案失敗：{str(e)}")
    
    def on_tree_select(self, event):
        """監聽表格選擇事件，記錄當前選中行"""
        selected_items = event.widget.selection() if event else self.tree.selection()
        if selected_items:
            self.current_selected_item = selected_items[0]
        else:
            self.current_selected_item = None
    
    def _create_edit_window(self, title, current_vals=None):
        """共用創建彈窗的邏輯，避免重複代碼"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("450x250" if current_vals else "450x220")
        window.resizable(False, False)
        # 置於螢幕中央
        window.transient(self.root)
        window.grab_set()
        x = (window.winfo_screenwidth() // 2) - (450 // 2)
        y = (window.winfo_screenheight() // 2) - (250 // 2 if current_vals else 220 // 2)
        window.geometry(f"+{x}+{y}")
        return window
    
    def edit_selected_row(self):
        """編輯選中的行數據 - 修復數據類型錯誤，增強驗證"""
        if not self.current_selected_item:
            messagebox.warning("警告", "請先選擇要編輯的行！")
            return
        
        # 获取选中行的当前值
        current_vals = self.tree.item(self.current_selected_item, 'values')
        if not current_vals:
            return
        
        # 使用共用方法創建彈窗
        edit_window = self._create_edit_window("編輯數據", current_vals)
        
        # 創建變數存儲輸入值（統一為字串，避免類型衝突）
        userid_var = tk.StringVar(value=str(current_vals[0]))
        username_var = tk.StringVar(value=str(current_vals[1]))
        cardno_var = tk.StringVar(value=str(current_vals[2]))
        
        # 設置界面樣式
        main_frame = ttk.Frame(edit_window, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. UserID 輸入框（不可編輯）
        ttk.Label(main_frame, text="UserID：", font=("Arial", 11)).grid(row=0, column=0, sticky=tk.W, pady=10)
        userid_entry = ttk.Entry(main_frame, textvariable=userid_var, width=30, font=("Arial", 11))
        userid_entry.grid(row=0, column=1, pady=10, padx=10)
        userid_entry.config(state="readonly")  # UserID不可編輯
        
        # 2. Username 輸入框
        ttk.Label(main_frame, text="使用者名稱：", font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, pady=10)
        username_entry = ttk.Entry(main_frame, textvariable=username_var, width=30, font=("Arial", 11))
        username_entry.grid(row=1, column=1, pady=10, padx=10)
        username_entry.focus_set()
        
        # 3. CardNo 輸入框（嚴格驗證7位數字）
        ttk.Label(main_frame, text="卡片號碼（7位數字）：", font=("Arial", 11)).grid(row=2, column=0, sticky=tk.W, pady=10)
        cardno_entry = ttk.Entry(main_frame, textvariable=cardno_var, width=30, font=("Arial", 11))
        cardno_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # 保存按鈕函數
        def save_edit():
            userid = userid_var.get().strip()
            username = username_var.get().strip()
            cardno = cardno_var.get().strip()
            
            # 驗證1：username非空
            if not username:
                messagebox.showwarning("驗證失敗", "使用者名稱不可為空！", parent=edit_window)
                username_entry.focus_set()
                return
            
            # 驗證2：cardno為7位數字（可選？原邏輯為必填，保持一致）
            if not cardno:
                messagebox.showwarning("驗證失敗", "卡片號碼不可為空！", parent=edit_window)
                cardno_entry.focus_set()
                return
            if not cardno.isdigit():
                messagebox.showwarning("驗證失敗", "卡片號碼必須為數字！", parent=edit_window)
                cardno_entry.focus_set()
                return
            if len(cardno) != 7:
                messagebox.showwarning("驗證失敗", "卡片號碼必須為7位數字！", parent=edit_window)
                cardno_entry.focus_set()
                return
            
            # 核心修復：更新底層數據時，用loc而非iloc，避免索引混亂+類型不匹配
            item_index = self.tree.index(self.current_selected_item)
            # 直接賦值字串，與DataFrame的字串類型完全匹配
            self.excel_data.loc[item_index, 'userid'] = userid
            self.excel_data.loc[item_index, 'username'] = username
            self.excel_data.loc[item_index, 'cardno'] = cardno
            
            # 更新表格顯示
            self.tree.item(self.current_selected_item, values=(userid, username, cardno))
            
            # 關閉編輯視窗
            edit_window.destroy()
            messagebox.showinfo("成功", "數據已更新！", parent=self.root)
        
        # 按鈕框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # 保存按鈕
        save_btn = ttk.Button(btn_frame, text="保存修改", command=save_edit, style="Accent.TButton")
        save_btn.pack(side=tk.LEFT, padx=10)
        
        # 取消按鈕
        cancel_btn = ttk.Button(btn_frame, text="取消", command=edit_window.destroy)
        cancel_btn.pack(side=tk.LEFT)

    def get_next_userid(self):
        """自動計算下一個遞補的UserID（最大現有ID +1）"""
        # 過濾出有效的數字UserID（兼容字串類型的DataFrame）
        valid_userids = []
        for uid in self.excel_data['userid']:
            if uid.strip().isdigit():
                valid_userids.append(int(uid.strip()))
        
        if not valid_userids:
            return 1  # 沒有有效ID時從1開始
        return max(valid_userids) + 1  # 最大ID +1

    def add_new_row(self):
        """新增一行數據 - 修復類型匹配，增強驗證"""
        # 自動生成下一個UserID
        next_userid = self.get_next_userid()
        
        # 使用共用方法創建彈窗
        add_window = self._create_edit_window("新增數據")
        
        # 創建變數存儲輸入值
        username_var = tk.StringVar()
        cardno_var = tk.StringVar()
        
        # 設置界面樣式
        main_frame = ttk.Frame(add_window, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. 顯示自動生成的UserID（不可編輯）
        ttk.Label(main_frame, text="自動分配UserID：", font=("Arial", 11)).grid(row=0, column=0, sticky=tk.W, pady=10)
        userid_label = ttk.Label(main_frame, text=str(next_userid), font=("Arial", 11, "bold"))
        userid_label.grid(row=0, column=1, pady=10, padx=10, sticky=tk.W)
        
        # 2. Username 輸入框（必填）
        ttk.Label(main_frame, text="使用者名稱（必填）：", font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, pady=10)
        username_entry = ttk.Entry(main_frame, textvariable=username_var, width=30, font=("Arial", 11))
        username_entry.grid(row=1, column=1, pady=10, padx=10)
        username_entry.focus_set()  # 預設焦點在使用者名稱
        
        # 3. CardNo 輸入框（必填，7位數字）
        ttk.Label(main_frame, text="卡片號碼（必填，7位數字）：", font=("Arial", 11)).grid(row=2, column=0, sticky=tk.W, pady=10)
        cardno_entry = ttk.Entry(main_frame, textvariable=cardno_var, width=30, font=("Arial", 11))
        cardno_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # 保存按鈕函數
        def save_new():
            username = username_var.get().strip()
            cardno = cardno_var.get().strip()
            userid = str(next_userid)  # 統一為字串
            
            # 驗證1：Username必填
            if not username:
                messagebox.showwarning("驗證失敗", "使用者名稱為必填欄位！", parent=add_window)
                username_entry.focus_set()
                return
            
            # 驗證2：CardNo必填且為7位數字
            if not cardno:
                messagebox.showwarning("驗證失敗", "卡片號碼為必填欄位！", parent=add_window)
                cardno_entry.focus_set()
                return
            if not cardno.isdigit():
                messagebox.showwarning("驗證失敗", "卡片號碼必須為數字！", parent=add_window)
                cardno_entry.focus_set()
                return
            if len(cardno) != 7:
                messagebox.showwarning("驗證失敗", "卡片號碼必須為7位數字！", parent=add_window)
                cardno_entry.focus_set()
                return
            
            # 驗證3：CardNo不能與已存在的重複（兼容字串類型）
            existing_cardnos = self.excel_data['cardno'].tolist()
            if cardno in existing_cardnos:
                messagebox.showwarning("驗證失敗", f"卡片號碼 {cardno} 已存在，請更換！", parent=add_window)
                cardno_entry.focus_set()
                return
            
            # 核心修復：新增行為字串類型，與原DataFrame完全一致
            new_row = pd.DataFrame(
                [[userid, username, cardno]], 
                columns=['userid', 'username', 'cardno'],
                dtype=str  # 強制指定字串類型，杜絕類型不匹配
            )
            self.excel_data = pd.concat([self.excel_data, new_row], ignore_index=True)
            
            # 添加到表格
            self.tree.insert('', tk.END, values=(userid, username, cardno))
            
            # 關閉新增視窗
            add_window.destroy()
            messagebox.showinfo("成功", f"新數據已新增！自動分配UserID：{userid}", parent=self.root)
        
        # 按鈕框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # 保存按鈕
        save_btn = ttk.Button(btn_frame, text="新增", command=save_new, style="Accent.TButton")
        save_btn.pack(side=tk.LEFT, padx=10)
        
        # 取消按鈕
        cancel_btn = ttk.Button(btn_frame, text="取消", command=add_window.destroy)
        cancel_btn.pack(side=tk.LEFT)
    
    def delete_selected_row(self):
        """刪除選中的行（本地Excel數據）"""
        if not self.current_selected_item:
            messagebox.warning("警告", "請先選擇要刪除的行！")
            return
        
        # 確認刪除
        if not messagebox.askyesno("確認", "確定要刪除選中的行嗎？"):
            return
        
        # 刪除表格中的行
        item_index = self.tree.index(self.current_selected_item)
        self.tree.delete(self.current_selected_item)
        
        # 刪除底層數據（兼容字串類型DataFrame）
        self.excel_data = self.excel_data.drop(self.excel_data.index[item_index]).reset_index(drop=True)
        
        # 清空選中狀態
        self.current_selected_item = None
    
    def save_excel_data(self):
        """保存修改後的數據回Excel文件"""
        try:
            self.excel_data.to_excel(self.user_list_var.get(), index=False)
            messagebox.showinfo("成功", "數據已保存回Excel檔案！")
        except Exception as e:
            messagebox.showerror("錯誤", f"保存Excel失敗：{str(e)}")
    
    def show_step2(self):
        """顯示第二步：展示並可編輯Excel數據"""
        # 清空當前界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 標題欄（默認黑色字體）
        title_label = ttk.Label(self.root, text="Step2:編輯用戶數據", font=("Arial", 14, "bold"))
        title_label.pack(pady=15)
        
        # 創建表格框架
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 垂直滾動條
        vscroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 水平滾動條
        hscroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 創建表格（默認黑色字體，移除所有自定義顏色）
        self.tree = ttk.Treeview(table_frame, columns=('userid', 'username', 'cardno'), 
                                show='headings', yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
        
        # 設置列標題（居中，默認黑色）
        self.tree.heading('userid', text='UserID', anchor=tk.CENTER)
        self.tree.heading('username', text='使用者名稱', anchor=tk.CENTER)
        self.tree.heading('cardno', text='卡片號碼', anchor=tk.CENTER)
        
        # 設置列寬和對齊方式（居中，默認黑色）
        self.tree.column('userid', width=80, anchor=tk.CENTER)
        self.tree.column('username', width=200, anchor=tk.CENTER)
        self.tree.column('cardno', width=150, anchor=tk.CENTER)
        
        # 填充數據（兼容字串類型DataFrame）
        for idx, row in self.excel_data.iterrows():
            self.tree.insert('', tk.END, values=(
                row['userid'],
                row['username'],
                row['cardno']
            ))
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 綁定滾動條
        vscroll.config(command=self.tree.yview)
        hscroll.config(command=self.tree.xview)
        
        # 綁定選擇事件
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # 按鈕框架
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 編輯按鈕
        edit_btn = ttk.Button(btn_frame, text="編輯選中行", command=self.edit_selected_row)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        # 新增按鈕
        add_btn = ttk.Button(btn_frame, text="新增行", command=self.add_new_row)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # 刪除按鈕
        delete_btn = ttk.Button(btn_frame, text="刪除選中行", command=self.delete_selected_row)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 保存按鈕
        save_btn = ttk.Button(btn_frame, text="保存修改到Excel", command=self.save_excel_data)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # 數據統計（默認黑色字體，強化顯示）
        count_label = ttk.Label(btn_frame, text=f"當前數據總數：{len(self.excel_data)} 條", font=("Arial", 10, "bold"))
        count_label.pack(side=tk.RIGHT, padx=5)
        
        # 底部按鈕區
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, pady=20)
        
        # 返回按鈕
        back_btn = ttk.Button(bottom_frame, text="返回上一步", command=self.show_step1)
        back_btn.pack(side=tk.LEFT, padx=10)
        
        # 下一步按鈕
        next_btn = ttk.Button(bottom_frame, text="下一步", command=self.go_to_step3, style="Accent.TButton")
        next_btn.pack(side=tk.RIGHT, padx=10)
    
    def check_port_occupied(self, port):
        """檢查指定端口是否被占用"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            result = sock.bind(('', port))
            sock.close()
            return False  # 端口未被占用
        except:
            return True  # 端口已被占用
    
    def update_php_delete_file(self, userid):
        """更新rfid_del_user.php文件中的$del_userid、$api_url、$tid"""
        ipc_ip = self.get_full_ipc()
        tid = self.tid_var.get().strip()  # 後台獲取TID，不對外用戶開放
        if not ipc_ip:
            messagebox.showerror("錯誤", "IPC IP配置不正確，無法更新PHP文件！")
            return False
        if not tid:
            messagebox.showerror("錯誤", "TID配置不正確，無法更新PHP文件！")
            return False
        
        if not os.path.exists(PHP_DELETE_FILE):
            messagebox.showerror("錯誤", f"找不到文件：{PHP_DELETE_FILE}")
            return False
        
        try:
            with open(PHP_DELETE_FILE, 'r', encoding='utf-8') as f:
                php_content = f.read()
            
            php_content = re.sub(r'\$del_userid\s*=\s*"[^"]+";', f'$del_userid = "{userid}";', php_content)
            php_content = re.sub(r'\$api_url\s*=\s*"http://[^"]+";', f'$api_url = "http://{ipc_ip}";', php_content)
            php_content = re.sub(r'\$tid\s*=\s*"[^"]+";', f'$tid = "{tid}";', php_content)
            
            with open(PHP_DELETE_FILE, 'w', encoding='utf-8') as f:
                f.write(php_content)
            
            return True
        except Exception as e:
            messagebox.showerror("錯誤", f"更新PHP文件失敗：{str(e)}")
            return False
    
    def update_php_all_delete_file(self):
        """更新rfid_all_del_user.php文件中的$api_url和$tid"""
        ipc_ip = self.get_full_ipc()
        tid = self.tid_var.get().strip()  # 後台獲取TID，不對外用戶開放
        if not ipc_ip or not tid:
            messagebox.showerror("錯誤", "IPC IP或TID配置不正確，無法更新PHP文件！")
            return False
        
        if not os.path.exists(PHP_ALL_DELETE_FILE):
            messagebox.showerror("錯誤", f"找不到文件：{PHP_ALL_DELETE_FILE}")
            return False
        
        try:
            with open(PHP_ALL_DELETE_FILE, 'r', encoding='utf-8') as f:
                php_content = f.read()
            
            php_content = re.sub(r'\$api_url\s*=\s*"http://[^"]+";', f'$api_url = "http://{ipc_ip}";', php_content)
            php_content = re.sub(r'\$tid\s*=\s*"[^"]+";', f'$tid = "{tid}";', php_content)
            
            with open(PHP_ALL_DELETE_FILE, 'w', encoding='utf-8') as f:
                f.write(php_content)
            
            return True
        except Exception as e:
            messagebox.showerror("錯誤", f"更新PHP文件失敗：{str(e)}")
            return False
    
    def update_php_register_file(self):
        """批量更新rfid_register_user.php的$user_list、$api_url、$default_tid"""
        ipc_ip = self.get_full_ipc()
        tid = self.tid_var.get().strip()  # 後台獲取TID，不對外用戶開放
        if not ipc_ip or not tid:
            messagebox.showerror("錯誤", "IPC IP或TID配置不正確，無法更新PHP文件！")
            return False
        
        if not os.path.exists(PHP_REGISTER_FILE):
            messagebox.showerror("錯誤", f"找不到文件：{PHP_REGISTER_FILE}")
            return False
        
        try:
            with open(PHP_REGISTER_FILE, 'r', encoding='utf-8') as f:
                php_content = f.read()
            
            # 替換基礎配置
            php_content = re.sub(r'\$api_url\s*=\s*"http://[^"]+";', f'$api_url = "http://{ipc_ip}";', php_content)
            php_content = re.sub(r'\$default_tid\s*=\s*"[^"]+";', f'$default_tid = "{tid}";', php_content)
            
            # 構建批量用戶列表
            user_list_lines = []
            for idx, row in self.excel_data.iterrows():
                userid = row['userid'].strip()
                username = row['username'].strip().replace('"', '\\"')  # 轉義雙引號
                cardno = row['cardno'].strip()
                user_list_lines.append(f'    ["userid" => "{userid}", "username" => "{username}", "cardno" => "{cardno}"],')
            
            user_list_str = "\n".join(user_list_lines)
            user_list_pattern = r'\$user_list\s*=\s*\[\s*([\s\S]*?)\];'
            php_content = re.sub(user_list_pattern, f'$user_list = [\n{user_list_str}\n];', php_content)
            
            with open(PHP_REGISTER_FILE, 'w', encoding='utf-8') as f:
                f.write(php_content)
            
            return True
        except Exception as e:
            messagebox.showerror("錯誤", f"更新PHP文件失敗：{str(e)}")
            return False
    
    def execute_url(self, url):
        """通用執行URL的函數（不關閉瀏覽器）"""
        try:
            subprocess.Popen(['start', url], shell=True)
            return True
        except Exception as e:
            messagebox.showerror("錯誤", f"執行URL失敗：{str(e)}")
            return False
    
    def execute_delete_url(self): return self.execute_url(DELETE_URL)
    def execute_all_delete_url(self): return self.execute_url(ALL_DELETE_URL)
    def execute_register_url(self): return self.execute_url(REGISTER_URL)
    
    def execute_test_url(self):
        """執行測試URL"""
        if self.execute_url(TEST_URL):
            messagebox.showinfo("成功", f"已打開測試頁面：{TEST_URL}", parent=self.root)
    
    def open_delete_selection_window(self):
        """打開個別刪除的數據選擇視窗"""
        delete_window = tk.Toplevel(self.root)
        delete_window.title("選擇要刪除的用戶")
        delete_window.geometry("500x400")
        delete_window.resizable(False, False)
        delete_window.transient(self.root)
        delete_window.grab_set()
        
        x = (delete_window.winfo_screenwidth() // 2) - 250
        y = (delete_window.winfo_screenheight() // 2) - 200
        delete_window.geometry(f"+{x}+{y}")
        
        table_frame = ttk.Frame(delete_window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        vscroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        hscroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        delete_tree = ttk.Treeview(table_frame, columns=('userid', 'username', 'cardno'), 
                                  show='headings', yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
        delete_tree.heading('userid', text='UserID', anchor=tk.CENTER)
        delete_tree.heading('username', text='使用者名稱', anchor=tk.CENTER)
        delete_tree.heading('cardno', text='卡片號碼', anchor=tk.CENTER)
        delete_tree.column('userid', width=80, anchor=tk.CENTER)
        delete_tree.column('username', width=200, anchor=tk.CENTER)
        delete_tree.column('cardno', width=150, anchor=tk.CENTER)
        
        for idx, row in self.excel_data.iterrows():
            delete_tree.insert('', tk.END, values=(row['userid'], row['username'], row['cardno']))
        
        delete_tree.pack(fill=tk.BOTH, expand=True)
        vscroll.config(command=delete_tree.yview)
        hscroll.config(command=delete_tree.xview)
        
        selected_item = None
        def on_delete_select(event):
            nonlocal selected_item
            selected_items = event.widget.selection()
            selected_item = selected_items[0] if selected_items else None
        delete_tree.bind('<<TreeviewSelect>>', on_delete_select)
        
        def confirm_delete():
            nonlocal selected_item
            current_selections = delete_tree.selection()
            if not current_selections:
                messagebox.warning("警告", "請先選擇要刪除的用戶！", parent=delete_window)
                return
            selected_item = current_selections[0]
            row_vals = delete_tree.item(selected_item, 'values')
            if not row_vals:
                messagebox.warning("警告", "選中的數據無效！", parent=delete_window)
                return
            userid = row_vals[0]
            
            if not messagebox.askyesno("確認刪除", f"確定要刪除UserID為 {userid} 的用戶嗎？", parent=delete_window):
                return
            
            if self.update_php_delete_file(userid) and self.execute_delete_url():
                messagebox.showinfo("成功", f"刪除操作已執行！\nUserID：{userid}\n已打開URL：{DELETE_URL}", parent=delete_window)
            
            delete_tree.selection_remove(selected_item)
            selected_item = None
        
        btn_frame = ttk.Frame(delete_window)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        confirm_btn = ttk.Button(btn_frame, text="確認刪除", command=confirm_delete, style="Accent.TButton")
        confirm_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = ttk.Button(btn_frame, text="取消", command=delete_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def reupload_function(self):
        """重新上傳功能：全量刪除後批量註冊"""
        if not messagebox.askyesno("確認", "確定要執行重新上傳操作嗎？\n操作將打開兩個瀏覽器頁面！"):
            return
        
        if self.update_php_all_delete_file():
            messagebox.showinfo("成功", "已更新全量刪除PHP配置！", parent=self.root)
            if self.execute_all_delete_url():
                messagebox.showinfo("成功", f"已執行全量刪除：{ALL_DELETE_URL}", parent=self.root)
        
        if self.update_php_register_file():
            messagebox.showinfo("成功", "已更新批量註冊PHP配置！", parent=self.root)
            if self.execute_register_url():
                messagebox.showinfo("成功", f"已執行批量註冊：{REGISTER_URL}", parent=self.root)
        
        messagebox.showinfo("完成", "重新上傳操作已全部執行！請確認瀏覽器頁面結果。", parent=self.root)
    
    def start_apache_xampp(self):
        """獨立的Apache/XAMPP啟動函數（供啟動按鈕調用）"""
        xampp_path = self.xampp_var.get()
        if not xampp_path or not os.path.exists(xampp_path):
            messagebox.warning("警告", "XAMPP路徑無效，請返回第一步重新配置！")
            return
        
        port_80_occupied = self.check_port_occupied(APACHE_DEFAULT_PORT)
        port_status_msg = f"80端口{'已被占用' if port_80_occupied else '未被占用'}"
        
        apache_bat_path = os.path.join(xampp_path, "apache_start.bat")
        apache_control_path = os.path.join(xampp_path, "xampp-control.exe")
        if not os.path.exists(apache_bat_path):
            apache_bat_path = os.path.join(xampp_path, "apache", "bin", "httpd.exe")
        
        files_check = []
        if not os.path.exists(apache_bat_path):
            files_check.append(f"Apache啟動文件：{apache_bat_path}")
        if not os.path.exists(apache_control_path):
            files_check.append(f"XAMPP控制面板：{apache_control_path}")
        
        if files_check:
            messagebox.showerror("錯誤", f"找不到以下文件：\n{chr(10).join(files_check)}")
            return
        
        try:
            # 啟動Apache和XAMPP控制面板
            subprocess.Popen(apache_bat_path, cwd=os.path.dirname(apache_bat_path), 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            subprocess.Popen(apache_control_path, cwd=os.path.dirname(apache_control_path),
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.attributes('-topmost', False)
            
            messagebox.showinfo(
                "Apache啟動成功", 
                f"✅ 已成功啟動Apache和XAMPP控制面板！\nℹ️ {port_status_msg}\n\n請在XAMPP控制面板中確認Apache是否正常運行。",
                parent=self.root
            )
        except Exception as e:
            messagebox.showerror("錯誤", f"啟動Apache/XAMPP失敗：{str(e)}")
    
    def stop_apache(self):
        """停止Apache服務"""
        xampp_path = self.xampp_var.get()
        if not xampp_path or not os.path.exists(xampp_path):
            messagebox.warning("警告", "XAMPP路徑無效，無法停止Apache！")
            return
        
        apache_stop_bat = os.path.join(xampp_path, "apache_stop.bat")
        try:
            if os.path.exists(apache_stop_bat):
                subprocess.Popen(apache_stop_bat, cwd=os.path.dirname(apache_stop_bat), 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(['cmd', '/c', 'net', 'stop', 'Apache2.4'], creationflags=subprocess.CREATE_NEW_CONSOLE)
            messagebox.showinfo("成功", "已執行Apache停止命令！")
        except Exception as e:
            messagebox.showerror("錯誤", f"停止Apache失敗：{str(e)}")
    
    def go_to_step3(self):
        """進入第三步：移除自動啟動，直接顯示Step3界面"""
        self.save_excel_data()
        # 校驗XAMPP路徑（僅提示，不阻擋進入Step3）
        xampp_path = self.xampp_var.get()
        if not xampp_path or not os.path.exists(xampp_path):
            messagebox.warning("警告", "XAMPP路徑尚未配置或無效，請在Step3中先配置再點擊啟動！")
        self.show_step3()
    
    def show_step3(self):
        """顯示第三步：Apache服務控制（保留啟動按鈕，原有功能不變）"""
        # 清空當前界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 將視窗置前
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)
        
        # 標題
        title_label = ttk.Label(self.root, text="Step3:Apache服務控制", font=("Arial", 16, "bold"))
        title_label.pack(pady=50)
        
        # 提示信息
        info_label = ttk.Label(self.root, text="✅ RFID后台上传工具已完成數據配置\n請點擊【啟動】按鈕開啟Apache和XAMPP服務", 
                            font=("Arial", 12), justify=tk.CENTER)
        info_label.pack(pady=20)
        
        # 功能按鈕框架（啟動按鈕首位，原有功能保留）
        func_btn_frame = ttk.Frame(self.root)
        func_btn_frame.pack(fill=tk.X, padx=50, pady=30)
        
        # 啟動按鈕（Apache/XAMPP啟動，放在功能區首位）
        start_btn = ttk.Button(func_btn_frame, text="啟動", command=self.start_apache_xampp, style="Accent.TButton")
        start_btn.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.X, expand=True)
        
        # 原有功能按鈕：個別刪除、重新上傳、測試
        delete_btn = ttk.Button(func_btn_frame, text="個別刪除", command=self.open_delete_selection_window, style="Accent.TButton")
        delete_btn.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.X, expand=True)
        
        reupload_btn = ttk.Button(func_btn_frame, text="重新上傳", command=self.reupload_function, style="Accent.TButton")
        reupload_btn.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.X, expand=True)
        
        test_btn = ttk.Button(func_btn_frame, text="測試", command=self.execute_test_url, style="Accent.TButton")
        test_btn.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.X, expand=True)
        
        # 底部按鈕區（上一步 + 完成）
        bottom_btn_frame = ttk.Frame(self.root)
        bottom_btn_frame.pack(side=tk.BOTTOM, pady=30)
        
        # 上一步按鈕（返回Step2）
        back_btn = ttk.Button(bottom_btn_frame, text="上一步", command=self.show_step2)
        back_btn.pack(side=tk.LEFT, padx=20)
        
        # 完成按鈕（停止Apache並退出）
        finish_btn = ttk.Button(bottom_btn_frame, text="完成", command=lambda: [self.stop_apache(), self.root.quit()], style="Accent.TButton")
        finish_btn.pack(side=tk.RIGHT, padx=20)


if __name__ == "__main__":
    # 安裝依賴（原有代碼不動）
    try:
        import psutil
    except ImportError:
        subprocess.check_call(["pip", "install", "psutil"])
        import psutil
    
    try:
        import pandas
        import openpyxl
    except ImportError:
        subprocess.check_call(["pip", "install", "pandas", "openpyxl"])
        import pandas
        import openpyxl
    
    # 根窗口配置 + 按鈕樣式（原有代碼）
    root = tk.Tk()
    # ========== 新增：設置程序icon（關鍵代碼） ==========
    root.iconbitmap("my_icon.ico")
    # ==================================================
    style = ttk.Style(root)
    style.configure("Accent.TButton", font=("Arial", 10, "bold"), background="#2196F3")
    style.map("Accent.TButton", background=[('active', '#1976D2')])
    
    app = RFIDUploadTool(root)
    root.mainloop()