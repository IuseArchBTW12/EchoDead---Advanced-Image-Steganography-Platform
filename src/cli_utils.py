#!/usr/bin/env python3
"""
Enhanced CLI utilities for beautiful terminal output
"""

try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback to no colors
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Back:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = BLACK = RESET = ""
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ""

import sys
import time

# Color scheme
class Colors:
    ERROR = Fore.RED
    SUCCESS = Fore.GREEN
    WARNING = Fore.YELLOW
    INFO = Fore.CYAN
    HEADER = Fore.MAGENTA
    HIGHLIGHT = Fore.YELLOW + Style.BRIGHT
    DIM = Style.DIM
    BOLD = Style.BRIGHT
    RESET = Style.RESET_ALL

def print_banner():
    """Print awesome ASCII banner"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   {Fore.MAGENTA}███████╗ ██████╗██╗  ██╗ ██████╗ ██████╗ ███████╗ █████╗ ██████╗  {Fore.CYAN}║
║   {Fore.MAGENTA}██╔════╝██╔════╝██║  ██║██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗ {Fore.CYAN}║
║   {Fore.MAGENTA}█████╗  ██║     ███████║██║   ██║██║  ██║█████╗  ███████║██║  ██║ {Fore.CYAN}║
║   {Fore.MAGENTA}██╔══╝  ██║     ██╔══██║██║   ██║██║  ██║██╔══╝  ██╔══██║██║  ██║ {Fore.CYAN}║
║   {Fore.MAGENTA}███████╗╚██████╗██║  ██║╚██████╔╝██████╔╝███████╗██║  ██║██████╔╝ {Fore.CYAN}║
║   {Fore.MAGENTA}╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═════╝  {Fore.CYAN}║
║                                                                       ║
║           {Fore.YELLOW}Hacktivist-Grade Image Steganography Tool{Fore.CYAN}               ║
║               {Fore.GREEN}[{Fore.WHITE}Encrypted{Fore.GREEN}] [{Fore.WHITE}Obfuscated{Fore.GREEN}] [{Fore.WHITE}Untraceable{Fore.GREEN}]{Fore.CYAN}               ║
║                    {Fore.RED}⚡ Inspired by DedSec ⚡{Fore.CYAN}                        ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def print_section_header(title):
    """Print a formatted section header"""
    width = 75
    print(f"\n{Fore.CYAN}{'━' * width}")
    print(f"{Fore.YELLOW}{Style.BRIGHT}{title.center(width)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'━' * width}{Style.RESET_ALL}\n")

def print_success(message):
    """Print success message"""
    print(f"{Colors.SUCCESS}✓{Style.RESET_ALL} {message}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.ERROR}✗{Style.RESET_ALL} {message}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠{Style.RESET_ALL} {message}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.INFO}ℹ{Style.RESET_ALL} {message}")

def print_step(step_num, total_steps, message):
    """Print a step in a process"""
    print(f"{Fore.MAGENTA}[{step_num}/{total_steps}]{Style.RESET_ALL} {message}")

def print_progress_bar(current, total, prefix='Progress', bar_length=50):
    """Print a progress bar"""
    percent = current / total
    filled = int(bar_length * percent)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f'\r{Colors.INFO}{prefix}{Style.RESET_ALL} |{Fore.GREEN}{bar}{Style.RESET_ALL}| {percent*100:.1f}%', end='', flush=True)
    if current == total:
        print()

def print_table(headers, rows):
    """Print a formatted table"""
    if not rows:
        print(f"{Colors.DIM}  (No items){Style.RESET_ALL}")
        return
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print header
    header_row = " │ ".join([h.ljust(col_widths[i]) for i, h in enumerate(headers)])
    print(f"{Fore.CYAN}{Style.BRIGHT}{header_row}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * (sum(col_widths) + len(headers) * 3 - 3)}{Style.RESET_ALL}")
    
    # Print rows
    for row in rows:
        row_str = " │ ".join([str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)])
        print(f"{Colors.DIM}{row_str}{Style.RESET_ALL}")

def print_key_value(key, value, indent=2):
    """Print key-value pair"""
    spaces = " " * indent
    print(f"{spaces}{Fore.CYAN}{key}:{Style.RESET_ALL} {Fore.WHITE}{value}{Style.RESET_ALL}")

def print_spinner(message, duration=2):
    """Show a spinner animation"""
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    idx = 0
    
    while time.time() < end_time:
        print(f'\r{Colors.INFO}{spinner[idx % len(spinner)]}{Style.RESET_ALL} {message}...', end='', flush=True)
        time.sleep(0.1)
        idx += 1
    
    print(f'\r{Colors.SUCCESS}✓{Style.RESET_ALL} {message}... Done!{" " * 20}')

def print_menu(title, options):
    """Print a formatted menu"""
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}{title}{Style.RESET_ALL}\n")
    
    for i, (key, description) in enumerate(options, 1):
        if key.lower() == 'exit' or key.lower() == 'back':
            color = Fore.RED
        elif key.lower() in ['workflow', 'quick', 'all-in-one']:
            color = Fore.GREEN + Style.BRIGHT
        else:
            color = Fore.WHITE
        
        print(f"  {Fore.CYAN}[{color}{key}{Fore.CYAN}]{Style.RESET_ALL} {description}")

def print_box(title, content, color=Fore.CYAN):
    """Print content in a box"""
    lines = content.split('\n')
    max_length = max(len(line) for line in lines)
    max_length = max(max_length, len(title))
    width = max_length + 4
    
    print(f"\n{color}┌{'─' * (width - 2)}┐")
    print(f"│ {Style.BRIGHT}{title.center(width - 4)}{Style.RESET_ALL}{color} │")
    print(f"├{'─' * (width - 2)}┤")
    
    for line in lines:
        print(f"│ {line.ljust(width - 4)} │")
    
    print(f"└{'─' * (width - 2)}┘{Style.RESET_ALL}\n")

def prompt_input(message, default=None, password=False):
    """Prompt for user input with styling"""
    if default:
        prompt = f"{Colors.HIGHLIGHT}❯{Style.RESET_ALL} {message} {Colors.DIM}[{default}]{Style.RESET_ALL}: "
    else:
        prompt = f"{Colors.HIGHLIGHT}❯{Style.RESET_ALL} {message}: "
    
    if password:
        import getpass
        return getpass.getpass(prompt)
    else:
        return input(prompt).strip()

def prompt_confirm(message, default=True):
    """Prompt for yes/no confirmation"""
    default_str = "Y/n" if default else "y/N"
    response = prompt_input(f"{message} ({default_str})", "").lower()
    
    if not response:
        return default
    return response in ['y', 'yes']

def clear_screen():
    """Clear the terminal screen"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

# Test function
if __name__ == "__main__":
    print_banner()
    print_section_header("Testing CLI Utilities")
    
    print_success("This is a success message")
    print_error("This is an error message")
    print_warning("This is a warning message")
    print_info("This is an info message")
    
    print("\nProgress bar test:")
    for i in range(101):
        print_progress_bar(i, 100, "Loading")
        time.sleep(0.02)
    
    print("\nSpinner test:")
    print_spinner("Processing data", 2)
    
    print("\nTable test:")
    print_table(
        ["Name", "Size", "Status"],
        [
            ["payload1.py", "2.5 KB", "✓ Ready"],
            ["payload2.py", "1.8 KB", "✓ Ready"],
            ["payload3.py", "3.2 KB", "⚠ Warning"]
        ]
    )
    
    print("\nKey-value test:")
    print_key_value("System", "Windows 10")
    print_key_value("Username", "john_doe")
    print_key_value("IP Address", "192.168.1.100")
    
    print_box("Important Notice", "This is a test message\nin a box\nwith multiple lines")
