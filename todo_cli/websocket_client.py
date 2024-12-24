import asyncio
import websockets
import sys
import termios
import tty
import select
import json
import shutil

class WebSocketShell:
    def __init__(self, url):
        self.url = url
        self.websocket = None
        self.original_settings = None
        self.command_buffer = ""
        self.terminal_size = shutil.get_terminal_size()
        self.is_connected = False

    def _set_raw_mode(self):
        """设置终端为raw模式，用于实时读取键盘输入"""
        self.original_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin)

    def _restore_terminal(self):
        """恢复终端设置"""
        if self.original_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.original_settings)

    async def _send_message(self, operation, data=None, **kwargs):
        """发送格式化的WebSocket消息"""
        message = {
            "operation": operation,
            "data": data,
            **kwargs
        }
        await self.websocket.send(json.dumps(message))

    async def _read_input(self):
        """从终端读取输入"""
        buffer = ""
        last_ch = None
        
        while True:
            if select.select([sys.stdin], [], [], 0)[0]:
                ch = sys.stdin.read(1)
                if ch:
                    # 处理特殊控制字符
                    if ord(ch) == 3:  # Ctrl+C
                        print("\n正在断开连接...")
                        return
                    elif ord(ch) == 4:  # Ctrl+D
                        if not buffer:  # 只在缓冲区为空时退出
                            print("\n正在断开连接...")
                            return
                    elif ch == '\r' or ch == '\n':  # Enter键
                        if last_ch != '\r' and last_ch != '\n':  # 避免重复处理CR/LF
                            cmd = buffer.strip()
                            if cmd == 'exit':
                                print("\n正在断开连接...")
                                return
                            if cmd:  # 只发送非空命令
                                print()  # 换行
                                yield {"operation": "stdin", "data": cmd + "\n"}
                            buffer = ""
                    else:
                        if ord(ch) >= 32:  # 只显示可打印字符
                            buffer += ch
                            sys.stdout.write(ch)
                            sys.stdout.flush()
                    last_ch = ch

    async def _handle_websocket_messages(self):
        """处理WebSocket消息"""
        try:
            async for message in self.websocket:
                try:
                    msg = json.loads(message)
                    if msg.get("operation") == "stdout":
                        data = msg.get("data", "")
                        if isinstance(data, str):
                            sys.stdout.write(data)
                            sys.stdout.flush()
                    else:
                        print(f"\r\n未知操作: {msg}", file=sys.stderr)
                except json.JSONDecodeError:
                    # 如果不是JSON格式，作为stdout处理
                    await self._send_message("stdout", message if isinstance(message, str) else message.decode())
        except websockets.exceptions.ConnectionClosed:
            if self.is_connected:
                print("\n连接已关闭")
            self.is_connected = False
            return

    async def _handle_terminal_resize(self):
        """处理终端大小变化"""
        while self.is_connected:
            new_size = shutil.get_terminal_size()
            if (new_size.columns != self.terminal_size.columns or 
                new_size.lines != self.terminal_size.lines):
                self.terminal_size = new_size
                await self._send_message(
                    "resize",
                    cols=self.terminal_size.columns,
                    rows=self.terminal_size.lines
                )
            await asyncio.sleep(1)

    async def connect(self):
        """连接到WebSocket服务器并开始交互会话"""
        try:
            self.websocket = await websockets.connect(
                self.url,
                ping_interval=30,
                ping_timeout=10
            )
            self.is_connected = True
            print(f"已连接到 {self.url}")
            print("提示: 输入'exit'或按Ctrl+C退出连接\n")
            
            # 发送初始化命令
            await self._send_message("stdin", data="\r")
            
            # 发送终端大小
            await self._send_message(
                "resize",
                cols=self.terminal_size.columns,
                rows=self.terminal_size.lines
            )
            
            self._set_raw_mode()
            
            try:
                # 创建消息处理和终端大小监控任务
                receive_task = asyncio.create_task(self._handle_websocket_messages())
                resize_task = asyncio.create_task(self._handle_terminal_resize())
                
                # 处理用户输入
                while self.is_connected:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        ch = sys.stdin.read(1)
                        if ch:
                            # 处理退出命令
                            if ch in ('\x03', '\x04'):  # Ctrl+C 或 Ctrl+D
                                break
                            
                            # 发送标准输入
                            await self._send_message("stdin", data=ch)
                
                # 取消后台任务
                for task in [receive_task, resize_task]:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            finally:
                self._restore_terminal()
                if self.websocket and not self.websocket.closed:
                    await self.websocket.close()
                    self.is_connected = False
        
        except Exception as e:
            print(f"连接错误: {str(e)}")
            self._restore_terminal()
            self.is_connected = False
            return
