import sys
import os
import inspect
from toolkit.accelerator import get_accelerator


def print_acc(*args, **kwargs):
    if get_accelerator().is_local_main_process:
        # 检查是否启用调试模式（通过环境变量控制）
        debug_print = os.environ.get('AI_TOOLKIT_DEBUG_PRINT', 'false').lower() == 'true'

        if debug_print:
            # 获取调用者信息
            frame = inspect.currentframe()
            try:
                # 获取调用 print_acc 的上一层调用栈
                caller_frame = frame.f_back
                if caller_frame:
                    filename = os.path.basename(caller_frame.f_code.co_filename)
                    line_number = caller_frame.f_lineno

                    # 如果调用者是 print_and_status_update，再往上一层找真正的调用者
                    if caller_frame.f_code.co_name == 'print_and_status_update':
                        real_caller_frame = caller_frame.f_back
                        if real_caller_frame:
                            filename = os.path.basename(real_caller_frame.f_code.co_filename)
                            line_number = real_caller_frame.f_lineno

                    # 在消息前添加文件名和行号
                    if args:
                        first_arg = f"[{filename}:{line_number}] {args[0]}"
                        print(first_arg, *args[1:], **kwargs)
                    else:
                        print(f"[{filename}:{line_number}]", **kwargs)
                else:
                    print(*args, **kwargs)
            finally:
                del frame
        else:
            # 正常输出，不添加调试信息
            print(*args, **kwargs)


class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'a')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()  # Make sure it's written immediately

    def flush(self):
        self.terminal.flush()
        self.log.flush()


def setup_log_to_file(filename):
    if get_accelerator().is_local_main_process:
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
    sys.stdout = Logger(filename)
    sys.stderr = Logger(filename)
