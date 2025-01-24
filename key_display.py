import tkinter as tk
from pynput import keyboard
import threading
import time

class KeyDisplayApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("按键显示")
        
        # 设置窗口始终置顶
        self.root.wm_attributes('-topmost', True)
        
        # 设置窗口透明度
        self.root.attributes('-alpha', 0.94)
        
        # 设置窗口大小和位置
        self.root.geometry("440x160+100+100")
        
        # 创建左右分隔框架
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        
        # 右侧框架固定宽度
        self.right_frame = tk.Frame(self.root, width=120)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)
        self.right_frame.pack_propagate(False)  # 防止子组件改变框架大小
        
        # 创建当前按键标签
        self.label = tk.Label(
            self.left_frame,
            text="等待按键...",
            font=("Arial", 20),
            wraplength=280
        )
        self.label.pack(expand=True)
        
        # 创建历史记录标签
        self.history_label = tk.Label(
            self.right_frame,
            text="按键历史",
            font=("Arial", 11),
            justify=tk.LEFT
        )
        self.history_label.pack(pady=5)
        
        # 创建历史记录文本框
        self.history_text = tk.Text(
            self.right_frame,
            font=("Arial", 12),
            width=20,  # 减小宽度
            height=20,
            state=tk.DISABLED,
            wrap=tk.WORD  # 添加自动换行
        )
        self.history_text.pack(expand=True, fill=tk.BOTH, padx=5)
        
        # 记录当前按下的键和最后按键时间
        self.current_keys = set()
        self.displayed_keys = set()
        self.last_key_time = 0
        self.display_duration = 1
        self.key_history = []  # 存储历史按键
        self.max_history = 50  # 最大历史记录数
        
        # 特殊按键映射
        self.key_map = {
            'ctrl_l': 'Ctrl',
            'ctrl_r': 'Ctrl',
            'shift_l': 'Shift',
            'shift_r': 'Shift',
            'alt_l': 'Alt',
            'alt_r': 'Alt',
            'space': 'Space',
            'enter': 'Enter',
            'esc': 'Esc',
            'tab': 'Tab',
            'backspace': 'Backspace',
            'delete': 'Delete',
            'up': '↑',
            'down': '↓',
            'left': '←',
            'right': '→',
            'page_up': 'PgUp',
            'page_down': 'PgDn',
            'home': 'Home',
            'end': 'End',
            'insert': 'Insert',
            'num_lock': 'NumLock',
            'caps_lock': 'CapsLock',
            'scroll_lock': 'ScrollLock',
            'print_screen': 'PrtSc',
            'pause': 'Pause'
        }
        
        # 启动键盘监听
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()
        
        # 启动定时检查线程
        self.check_thread = threading.Thread(target=self.check_key_timeout, daemon=True)
        self.check_thread.start()
        
    def get_key_name(self, key):
        """统一处理按键名称的方法"""
        try:
            # 处理特殊键
            if isinstance(key, keyboard.Key):
                key_str = str(key).replace('Key.', '')
                return self.key_map.get(key_str, key_str.upper())
            
            # 处理字符键
            if isinstance(key, keyboard.KeyCode):
                # 处理控制键组合
                if hasattr(key, 'vk') and key.vk:
                    if 65 <= key.vk <= 90:  # A-Z的虚拟键码范围
                        return chr(key.vk)
                    if 48 <= key.vk <= 57:  # 0-9的虚拟键码范围
                        return chr(key.vk)
                
                # 处理普通字符键
                if hasattr(key, 'char') and key.char:
                    if key.char.isprintable():
                        return key.char.upper()
            
            return None  # 忽略其他不需要显示的按键
            
        except (AttributeError, ValueError):
            return None
    
    def on_press(self, key):
        # 获取按键名称
        key_name = self.get_key_name(key)
        # 如果按键名称有效
        if key_name:  # 只处理有效的按键名称
            # 更新当前按键集合
            self.current_keys.add(key_name)
            # 复制当前按键集合到显示集合
            self.displayed_keys = self.current_keys.copy()
            # 更新最后按键时间
            self.last_key_time = time.time()
            # 更新显示
            self.update_display()
    
    def on_release(self, key):
        key_name = self.get_key_name(key)
        if key_name:  # 只处理有效的按键名称
            # 从当前按键集合中移除
            self.current_keys.discard(key_name)
    

    def check_key_timeout(self):
        while True:
            if self.displayed_keys and time.time() - self.last_key_time > self.display_duration:
                self.displayed_keys.clear()
                self.root.after(0, self.update_display)
            time.sleep(0.1)
    
    def update_history(self, key_text):
        """更新历史记录"""
        # 添加新的按键记录
        self.key_history.append(key_text)
        # 保持历史记录在最大限制内
        if len(self.key_history) > self.max_history:
            self.key_history = self.key_history[-self.max_history:]
        
        # 更新历史记录显示
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        for hist in reversed(self.key_history):  # 最新的显示在上面
            self.history_text.insert(tk.END, f"{hist}\n")
        self.history_text.config(state=tk.DISABLED)
    
    def update_display(self):
        if self.displayed_keys:
            # 将显示的按键分为控制键和普通字符键
            control_keys = {k for k in self.displayed_keys if k in ['Ctrl', 'Alt', 'Shift']}
            char_keys = {k for k in self.displayed_keys if k not in ['Ctrl', 'Alt', 'Shift']}
            
            # 检查是否只有字母数字键（没有控制键）
            only_alphanumeric = len(control_keys) == 0 and all(k.isalnum() for k in char_keys)
            
            if only_alphanumeric:
                # 如果只有字母数字键，显示最后一个按下的键
                display_text = list(char_keys)[-1] if char_keys else ""
            else:
                # 如果有控制键，显示组合键
                def sort_key(k):
                    # 控制键排在前面
                    if k in ['Ctrl', 'Alt', 'Shift']:
                        return (0, k)
                    # 其他键按字母顺序排序
                    return (1, k)
                
                display_text = ' + '.join(sorted(self.displayed_keys, key=sort_key))
            
            # 更新历史记录
            if display_text:
                self.update_history(display_text)
        else:
            display_text = "等待按键..."
            # 清空按键历史集合
            self.current_keys.clear()
            self.displayed_keys.clear()
            
        # 在主线程中更新标签文本
        self.root.after(0, lambda: self.label.config(text=display_text))
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = KeyDisplayApp()
    app.run() 

