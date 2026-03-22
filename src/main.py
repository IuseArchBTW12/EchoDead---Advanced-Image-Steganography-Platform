from PIL import Image
import subprocess
import sys
import os
import json
from pathlib import Path
import getpass
import time

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = WHITE = RESET = ""
    class Style:
        RESET_ALL = ""

# Import our custom modules
from cli_utils import (
    print_banner, print_success, print_error, print_warning, print_info,
    print_progress_bar, print_table, print_menu, prompt_input, prompt_confirm,
    print_section_header, print_spinner
)
from crypto_utils import (
    PayloadEncryption, create_encrypted_payload, extract_encrypted_payload,
    AntiAnalysis
)

# Configuration file paths
CONFIG_DIR = Path.home() / ".image_stego"
CONFIG_FILE = CONFIG_DIR / "config.json"
PAYLOADS_DIR = CONFIG_DIR / "payloads"

def initialize_config():
    """Initialize configuration directory and files"""
    CONFIG_DIR.mkdir(exist_ok=True)
    PAYLOADS_DIR.mkdir(exist_ok=True)
    
    if not CONFIG_FILE.exists():
        default_config = {
            "default_image": "",
            "default_output": "output_image.png",
            "auto_run": False,
            "recent_payloads": [],
            "encryption_enabled": False,
            "use_compression": True,
            "stealth_mode": False
        }
        save_config(default_config)
        print_info("Configuration initialized")
    
    return load_config()

def load_config():
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def list_payloads():
    """List all saved payloads"""
    payloads = list(PAYLOADS_DIR.glob("*.py"))
    return [(p.stem, p) for p in payloads]

def save_payload(name, code):
    """Save a payload to the library"""
    payload_path = PAYLOADS_DIR / f"{name}.py"
    with open(payload_path, 'w') as f:
        f.write(code)
    print_success(f"Payload '{name}' saved to library")
    return payload_path

def create_payload_from_file(source_path, name=None):
    """Copy a payload file to the library"""
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source file not found: {source_path}")
    
    if name is None:
        name = Path(source_path).stem
    
    with open(source_path, 'r') as f:
        code = f.read()
    
    return save_payload(name, code)


def embed_code_in_image(image_path, code_path, output_image_path, password=None, compress=True):
    try:
        print_section_header("EMBEDDING PAYLOAD")
        
        # Open the image in RGB mode
        print_info(f"Opening image: {image_path}")
        img = Image.open(image_path).convert('RGB')
        width, height = img.size
        print_success(f"Image loaded: {width}x{height} pixels")
        
        # Read the binary data from the code file
        print_info(f"Reading payload: {code_path}")
        with open(code_path, 'rb') as code_file:
            code_bytes = code_file.read()
        original_size = len(code_bytes)
        print_success(f"Payload loaded: {original_size} bytes")
        
        # Optional encryption/compression
        if password or compress:
            print_info("Applying encryption/compression...")
            code_bytes = create_encrypted_payload(
                code_bytes, 
                password=password,
                compress=compress
            )
            final_size = len(code_bytes)
            if compress and not password:
                print_success(f"Compressed: {original_size} → {final_size} bytes ({100 - (final_size*100//original_size)}% reduction)")
            elif password:
                print_success(f"Encrypted & compressed: {original_size} → {final_size} bytes")
        
        # Store file size as first 64 bits (8 bytes) - supports files up to 2^64 bytes
        file_size = len(code_bytes)
        size_bytes = file_size.to_bytes(8, byteorder='big')
        
        # Calculate total bits needed (size header + actual data)
        total_bytes = size_bytes + code_bytes
        code_bits = [bit for byte in total_bytes for bit in format(byte, '08b')]
        
        # Validate image capacity (3 bits per pixel)
        max_bits = width * height * 3
        if len(code_bits) > max_bits:
            print_error(f"Image too small! Need {len(code_bits)} bits but image can hold {max_bits} bits.")
            print_warning(f"Required image size: {len(code_bits) // 3} pixels minimum")
            raise ValueError("Image capacity exceeded")
        
        capacity_percent = (len(code_bits)*100//max_bits)
        print_info(f"Capacity: {len(code_bits):,}/{max_bits:,} bits ({capacity_percent}%)")
        
        # Embed the bits into the image pixels with progress bar
        print_info("Embedding data into pixels...")
        pixel_index = 0
        total_pixels = width * height
        
        for row in range(height):
            # Update progress bar every 10 rows
            if row % 10 == 0:
                current_pixel = row * width
                print_progress_bar(current_pixel, total_pixels, prefix='Embedding')
            
            for col in range(width):
                r, g, b = img.getpixel((col, row))
                if pixel_index < len(code_bits):
                    r = (r & ~1) | int(code_bits[pixel_index])
                    pixel_index += 1
                if pixel_index < len(code_bits):
                    g = (g & ~1) | int(code_bits[pixel_index])
                    pixel_index += 1
                if pixel_index < len(code_bits):
                    b = (b & ~1) | int(code_bits[pixel_index])
                    pixel_index += 1
                
                img.putpixel((col, row), (r, g, b))
        
        print_progress_bar(total_pixels, total_pixels, prefix='Embedding')
        print()  # New line after progress bar
        
        # Save the modified image
        print_info(f"Saving to: {output_image_path}")
        img.save(output_image_path)
        print_success("✓ Successfully embedded payload into image!")
        
    except FileNotFoundError as e:
        print_error(f"File not found: {e}")
        raise
    except ValueError as e:
        print_error(str(e))
        raise
    except Exception as e:
        print_error(f"Unexpected error during embedding: {e}")
        raise

def extract_code_from_image(image_path, output_code_path, password=None):
    try:
        print_section_header("EXTRACTING PAYLOAD")
        
        # Open the image in RGB mode
        print_info(f"Opening image: {image_path}")
        img = Image.open(image_path).convert('RGB')
        width, height = img.size
        print_success(f"Image loaded: {width}x{height} pixels")
        
        # First, extract the file size (first 64 bits = 8 bytes)
        print_info("Reading file size header...")
        size_bits = []
        pixel_count = 0
        
        for row in range(height):
            for col in range(width):
                r, g, b = img.getpixel((col, row))
                size_bits.append(str(r & 1))
                size_bits.append(str(g & 1))
                size_bits.append(str(b & 1))
                
                pixel_count += 1
                # Stop after extracting 64 bits (8 bytes) for file size
                if len(size_bits) >= 64:
                    break
            if len(size_bits) >= 64:
                break
        
        # Convert first 64 bits to file size
        size_bytes = bytearray(int(''.join(size_bits[i:i+8]), 2) for i in range(0, 64, 8))
        file_size = int.from_bytes(size_bytes, byteorder='big')
        
        print_success(f"Payload size: {file_size:,} bytes")
        
        # Calculate total bits needed (64 for size + file_size * 8 for data)
        total_bits_needed = 64 + (file_size * 8)
        
        # Extract all bits including size header with progress
        print_info("Extracting data from pixels...")
        code_bits = []
        total_pixels = width * height
        
        for row in range(height):
            # Update progress bar every 10 rows
            if row % 10 == 0 and total_bits_needed > 0:
                current_bits = len(code_bits)
                print_progress_bar(current_bits, total_bits_needed, prefix='Extracting')
            
            for col in range(width):
                r, g, b = img.getpixel((col, row))
                code_bits.append(str(r & 1))
                code_bits.append(str(g & 1))
                code_bits.append(str(b & 1))
                
                # Stop when we have enough bits
                if len(code_bits) >= total_bits_needed:
                    break
            if len(code_bits) >= total_bits_needed:
                break
        
        print_progress_bar(total_bits_needed, total_bits_needed, prefix='Extracting')
        print()  # New line after progress bar
        
        # Skip the first 64 bits (size header) and convert remaining bits to bytes
        data_bits = code_bits[64:total_bits_needed]
        code_bytes = bytearray(int(''.join(data_bits[i:i+8]), 2) for i in range(0, len(data_bits), 8))
        
        # Check if payload has encryption/compression flags (first byte)
        if len(code_bytes) > 0 and (code_bytes[0] & 0x03) != 0:  # Check for compression or encryption flags
            print_info("Detecting and processing compressed/encrypted payload...")
            try:
                original_size = len(code_bytes)
                code_bytes = extract_encrypted_payload(code_bytes, password=password)
                if len(code_bytes) != original_size:
                    print_success(f"Payload decompressed/decrypted: {original_size} → {len(code_bytes)} bytes")
            except Exception as e:
                print_error(f"Failed to decrypt/decompress: {e}")
                if password:
                    raise
                # If no password was provided, it might just be regular data
                print_warning("Continuing with raw extraction (might be corrupted)")
        
        # Write the binary data to a file
        print_info(f"Writing to: {output_code_path}")
        with open(output_code_path, 'wb') as code_file:
            code_file.write(code_bytes)
        
        print_success(f"✓ Successfully extracted payload ({len(code_bytes)} bytes)")
        
    except FileNotFoundError as e:
        print_error(f"File not found: {e}")
        raise
    except Exception as e:
        print_error(f"Unexpected error during extraction: {e}")
        raise

def run_extracted_code(code_path):
    try:
        print_section_header("EXECUTING PAYLOAD")
        print_warning("⚠ Running extracted code - ensure you trust the source!")
        
        # Run the extracted code using subprocess
        print_info(f"Executing: {code_path}")
        result = subprocess.run(['python', code_path], capture_output=True, text=True, timeout=30)
        
        print_section_header("EXECUTION OUTPUT")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print_warning("Standard Error:")
            print(result.stderr)
        
        if result.returncode == 0:
            print_success(f"✓ Execution completed successfully (Exit Code: {result.returncode})")
        else:
            print_error(f"Execution failed (Exit Code: {result.returncode})")
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print_error("Code execution timed out (30s limit)")
        raise
    except FileNotFoundError:
        print_error("Python interpreter not found. Make sure Python is in your PATH.")
        raise
    except Exception as e:
        print_error(f"Unexpected error during execution: {e}")
        raise

def quick_workflow(image_path, payload_path, output_image=None, auto_run=False, password=None, compress=True):
    """Complete workflow: embed -> extract -> optionally run"""
    print_banner()
    print_section_header("QUICK WORKFLOW: Embed → Extract → Run")
    
    if output_image is None:
        output_image = "temp_output.png"
    
    extracted_path = "temp_extracted.py"
    
    try:
        # Step 1: Embed
        print_info("\n[STEP 1/3] Embedding payload...")
        embed_code_in_image(image_path, payload_path, output_image, password=password, compress=compress)
        
        # Step 2: Extract
        print_info("\n[STEP 2/3] Extracting payload to verify...")
        extract_code_from_image(output_image, extracted_path, password=password)
        
        # Step 3: Run (optional)
        if auto_run:
            print_info("\n[STEP 3/3] Running payload...")
            run_extracted_code(extracted_path)
        else:
            print_warning("\n[STEP 3/3] Skipped (auto_run disabled)")
        
        print_section_header("WORKFLOW COMPLETE")
        print_success(f"Output image: {output_image}")
        print_success(f"Extracted code: {extracted_path}")
        
    except Exception as e:
        print_error(f"Workflow failed: {e}")
        raise

def interactive_menu():
    """Interactive CLI menu"""
    config = initialize_config()
    
    # Show banner once at startup
    print_banner()
    
    while True:
        print_section_header("ECHODEAD")
        
        menu_options = [
            ("Quick Workflow", "Embed → Extract → Run"),
            ("Embed Payload", "Hide payload in image"),
            ("Extract Payload", "Extract payload from image"),
            ("Payload Management", "Manage payload library"),
            ("Settings", "Configure tool options"),
            ("Exit", "Quit application")
        ]
        
        print_menu("Select option", menu_options)
        choice = int(input(f"\n{Fore.CYAN}Enter choice (1-6): {Style.RESET_ALL}"))
        
        if choice == 1:
            handle_quick_workflow(config)
        elif choice == 2:
            handle_embed(config)
        elif choice == 3:
            handle_extract(config)
        elif choice == 4:
            handle_payload_management(config)
        elif choice == 5:
            handle_settings(config)
        elif choice == 6:
            print_info("\nExiting...")
            break
        else:
            print_error("Invalid option. Try again.")

def handle_quick_workflow(config):
    """Handle quick workflow option"""
    print_section_header("Quick Workflow")
    
    # Select image
    if config.get("default_image") and os.path.exists(config["default_image"]):
        if prompt_confirm(f"Use default image '{config['default_image']}'?"):
            image_path = config["default_image"]
        else:
            image_path = prompt_input("Enter image path")
    else:
        image_path = prompt_input("Enter image path")
    
    # Select payload
    payloads = list_payloads()
    if payloads:
        print_info("\nAvailable payloads:")
        # Create a simplified list for print_table
        payload_data = [[str(i+1), name, f"{path.stat().st_size} bytes"] 
                        for i, (name, path) in enumerate(payloads)]
        print_table(["#", "Name", "Size"], payload_data)
        
        print_info("[0] Use custom file")
        
        payload_choice = prompt_input("\nSelect payload number")
        if payload_choice == "0":
            payload_path = prompt_input("Enter payload file path")
        else:
            try:
                idx = int(payload_choice) - 1
                payload_path = str(payloads[idx][1])
            except (ValueError, IndexError):
                print_error("Invalid selection.")
                return
    else:
        payload_path = prompt_input("Enter payload file path")
    
    output_image = prompt_input(f"Output image name", default=config.get('default_output', 'output.png'))
    
    # Encryption option
    use_encryption = config.get('encryption_enabled', False)
    if prompt_confirm(f"Enable encryption?", default=use_encryption):
        password = getpass.getpass("Enter encryption password: ")
        if not password:
            print_warning("No password provided, skipping encryption")
            password = None
    else:
        password = None
    
    # Compression option
    use_compression = config.get('use_compression', True)
    compress = prompt_confirm("Enable compression?", default=use_compression)
    
    # Auto-run option
    auto_run = config.get('auto_run', False)
    auto_run = prompt_confirm("Run payload after extraction?", default=auto_run)
    
    try:
        quick_workflow(image_path, payload_path, output_image, auto_run, password=password, compress=compress)
    except Exception:
        pass

def handle_embed(config):
    """Handle embed option"""
    print_section_header("Embed Payload")
    
    image_path = prompt_input("Enter image path")
    payload_path = prompt_input("Enter payload file path")
    output_path = prompt_input("Enter output image path")
    
    # Encryption option
    if prompt_confirm("Enable encryption?", default=config.get('encryption_enabled', False)):
        password = getpass.getpass("Enter encryption password: ")
    else:
        password = None
    
    # Compression option
    compress = prompt_confirm("Enable compression?", default=config.get('use_compression', True))
    
    try:
        embed_code_in_image(image_path, payload_path, output_path, password=password, compress=compress)
    except Exception:
        pass

def handle_extract(config):
    """Handle extract option"""
    print_section_header("Extract Payload")
    
    image_path = prompt_input("Enter image path")
    output_path = prompt_input("Enter output file path")
    
    # Check if encrypted
    if prompt_confirm("Is payload encrypted?", default=config.get('encryption_enabled', False)):
        password = getpass.getpass("Enter decryption password: ")
    else:
        password = None
    
    try:
        extract_code_from_image(image_path, output_path, password=password)
        
        if prompt_confirm("\nRun extracted code now?"):
            run_extracted_code(output_path)
    except Exception:
        pass

def handle_payload_management(config):
    """Handle payload management menu"""
    while True:
        print_section_header("Payload Management")
        
        menu_options = [
            ("List Payloads", "View all saved payloads"),
            ("Add Payload", "Add from file"),
            ("Create New", "Create new payload"),
            ("Delete Payload", "Remove from library"),
            ("View Payload", "Display payload code"),
            ("Back", "Return to main menu")
        ]
        
        choice = print_menu(menu_options, "Select option")
        
        if choice == 1:
            payloads = list_payloads()
            if payloads:
                print_success("\nSaved Payloads:")
                payload_data = [[name, f"{path.stat().st_size} bytes", 
                                str(path.relative_to(PAYLOADS_DIR))] 
                               for name, path in payloads]
                print_table(["Name", "Size", "Location"], payload_data)
            else:
                print_warning("\nNo payloads saved yet.")
        
        elif choice == 2:
            source = prompt_input("Enter payload file path")
            name = prompt_input("Enter name for payload (leave empty for auto-name)", default="")
            name = name if name else None
            try:
                create_payload_from_file(source, name)
            except Exception as e:
                print_error(f"Error: {e}")
        
        elif choice == 3:
            name = prompt_input("Enter payload name")
            print_info("Enter payload code (press Ctrl+Z then Enter on Windows, Ctrl+D on Unix when done):")
            code_lines = []
            try:
                while True:
                    line = input()
                    code_lines.append(line)
            except EOFError:
                pass
            code = "\n".join(code_lines)
            try:
                save_payload(name, code)
            except Exception as e:
                print_error(f"Error: {e}")
        
        elif choice == 4:
            payloads = list_payloads()
            if not payloads:
                print_warning("\nNo payloads to delete.")
                continue
            
            print_info("\nPayloads:")
            payload_data = [[str(i+1), name] for i, (name, path) in enumerate(payloads)]
            print_table(["#", "Name"], payload_data)
            
            del_choice = prompt_input("\nSelect payload number to delete")
            try:
                idx = int(del_choice) - 1
                name, path = payloads[idx]
                if prompt_confirm(f"Delete '{name}'?"):
                    path.unlink()
                    print_success(f"Deleted '{name}'")
            except (ValueError, IndexError):
                print_error("Invalid selection.")
            except Exception as e:
                print_error(f"Error: {e}")
        
        elif choice == 5:
            payloads = list_payloads()
            if not payloads:
                print_warning("\nNo payloads available.")
                continue
            
            print_info("\nPayloads:")
            payload_data = [[str(i+1), name] for i, (name, path) in enumerate(payloads)]
            print_table(["#", "Name"], payload_data)
            
            view_choice = prompt_input("\nSelect payload number to view")
            try:
                idx = int(view_choice) - 1
                name, path = payloads[idx]
                print_section_header(f"Payload: {name}")
                with open(path, 'r') as f:
                    print(f.read())
                print_section_header("End of Payload")
            except (ValueError, IndexError):
                print_error("Invalid selection.")
            except Exception as e:
                print_error(f"Error: {e}")
        
        elif choice == 6:
            break
        else:
            print_error("Invalid option.")

def handle_settings(config):
    """Handle settings menu"""
    print_section_header("Settings")
    
    # Display current settings in a table
    settings_data = [
        ["Default Image", config.get('default_image', '(not set)')],
        ["Default Output", config.get('default_output', 'output_image.png')],
        ["Auto Run", str(config.get('auto_run', False))],
        ["Encryption Enabled", str(config.get('encryption_enabled', False))],
        ["Use Compression", str(config.get('use_compression', True))],
        ["Stealth Mode", str(config.get('stealth_mode', False))]
    ]
    print_table(["Setting", "Value"], settings_data)
    
    menu_options = [
        ("Set Default Image", "Set default cover image"),
        ("Set Default Output", "Set default output name"),
        ("Toggle Auto Run", f"Currently: {config.get('auto_run', False)}"),
        ("Toggle Encryption", f"Currently: {config.get('encryption_enabled', False)}"),
        ("Toggle Compression", f"Currently: {config.get('use_compression', True)}"),
        ("Toggle Stealth Mode", f"Currently: {config.get('stealth_mode', False)}"),
        ("Back", "Return to main menu")
    ]
    
    choice = print_menu(menu_options, "Select option")
    
    if choice == 1:
        path = prompt_input("Enter default image path")
        if os.path.exists(path):
            config['default_image'] = path
            save_config(config)
            print_success("Default image set")
        else:
            print_error("File not found")
    
    elif choice == 2:
        name = prompt_input("Enter default output name")
        config['default_output'] = name
        save_config(config)
        print_success("Default output name set")
    
    elif choice == 3:
        config['auto_run'] = not config.get('auto_run', False)
        save_config(config)
        print_success(f"Auto run: {config['auto_run']}")
    
    elif choice == 4:
        config['encryption_enabled'] = not config.get('encryption_enabled', False)
        save_config(config)
        print_success(f"Encryption enabled: {config['encryption_enabled']}")
    
    elif choice == 5:
        config['use_compression'] = not config.get('use_compression', True)
        save_config(config)
        print_success(f"Use compression: {config['use_compression']}")
    
    elif choice == 6:
        config['stealth_mode'] = not config.get('stealth_mode', False)
        save_config(config)
        print_success(f"Stealth mode: {config['stealth_mode']}")
        if config['stealth_mode']:
            print_warning("Stealth mode enables anti-analysis features")


# Main execution
if __name__ == "__main__":
    # Initialize config
    config = initialize_config()
    
    # If no arguments, start interactive menu
    if len(sys.argv) == 1:
        try:
            interactive_menu()
        except KeyboardInterrupt:
            print("\n")
            print_info("Exiting...")
        sys.exit(0)
    
    # Command-line mode
    command = sys.argv[1].lower()
    
    try:
        if command == "embed":
            if len(sys.argv) < 5:
                print_error("Usage: python main.py embed <image_path> <code_path> <output_image_path> [--password <pass>] [--no-compress]")
                sys.exit(1)
            
            # Parse optional arguments
            password = None
            compress = True
            if "--password" in sys.argv:
                idx = sys.argv.index("--password")
                if idx + 1 < len(sys.argv):
                    password = sys.argv[idx + 1]
            if "--no-compress" in sys.argv:
                compress = False
            
            embed_code_in_image(sys.argv[2], sys.argv[3], sys.argv[4], password=password, compress=compress)
            
        elif command == "extract":
            if len(sys.argv) < 4:
                print_error("Usage: python main.py extract <image_path> <output_code_path> [--password <pass>]")
                sys.exit(1)
            
            # Parse optional password
            password = None
            if "--password" in sys.argv:
                idx = sys.argv.index("--password")
                if idx + 1 < len(sys.argv):
                    password = sys.argv[idx + 1]
            
            extract_code_from_image(sys.argv[2], sys.argv[3], password=password)
            
        elif command == "run":
            if len(sys.argv) != 3:
                print_error("Usage: python main.py run <code_path>")
                sys.exit(1)
            run_extracted_code(sys.argv[2])
        
        elif command == "workflow" or command == "quick":
            if len(sys.argv) < 4:
                print_error("Usage: python main.py workflow <image_path> <payload_path> [output_image] [--run] [--password <pass>] [--no-compress]")
                sys.exit(1)
            
            image = sys.argv[2]
            payload = sys.argv[3]
            output = sys.argv[4] if len(sys.argv) > 4 and not sys.argv[4].startswith('--') else "output.png"
            auto_run = "--run" in sys.argv
            
            # Parse optional arguments
            password = None
            compress = True
            if "--password" in sys.argv:
                idx = sys.argv.index("--password")
                if idx + 1 < len(sys.argv):
                    password = sys.argv[idx + 1]
            if "--no-compress" in sys.argv:
                compress = False
            
            quick_workflow(image, payload, output, auto_run, password=password, compress=compress)
        
        elif command == "payload":
            if len(sys.argv) < 3:
                print_info("Payload commands:")
                print("  python main.py payload list")
                print("  python main.py payload add <file_path> [name]")
                print("  python main.py payload view <name>")
                sys.exit(1)
            
            subcommand = sys.argv[2].lower()
            
            if subcommand == "list":
                payloads = list_payloads()
                if payloads:
                    print_success("\nSaved Payloads:")
                    payload_data = [[name, f"{path.stat().st_size} bytes"] for name, path in payloads]
                    print_table(["Name", "Size"], payload_data)
                else:
                    print_warning("\nNo payloads saved.")
            
            elif subcommand == "add":
                if len(sys.argv) < 4:
                    print_error("Usage: python main.py payload add <file_path> [name]")
                    sys.exit(1)
                source = sys.argv[3]
                name = sys.argv[4] if len(sys.argv) > 4 else None
                create_payload_from_file(source, name)
            
            elif subcommand == "view":
                if len(sys.argv) < 4:
                    print_error("Usage: python main.py payload view <name>")
                    sys.exit(1)
                name = sys.argv[3]
                payload_path = PAYLOADS_DIR / f"{name}.py"
                if payload_path.exists():
                    with open(payload_path, 'r') as f:
                        print(f.read())
                else:
                    print_error(f"Payload '{name}' not found.")
                    sys.exit(1)
        
        elif command == "config":
            if len(sys.argv) < 3:
                print_section_header("Current Configuration")
                config_data = [[key, str(value)] for key, value in config.items()]
                print_table(["Key", "Value"], config_data)
            else:
                subcommand = sys.argv[2].lower()
                if subcommand == "set" and len(sys.argv) == 5:
                    key = sys.argv[3]
                    value = sys.argv[4]
                    # Convert boolean strings
                    if value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
                    config[key] = value
                    save_config(config)
                    print_success(f"Set {key} = {value}")
                else:
                    print_error("Usage: python main.py config set <key> <value>")
        
        elif command == "help" or command == "-h" or command == "--help":
            print_banner()
            print_section_header("ECHODEAD - HELP")
            
            print_info("\nInteractive Mode:")
            print("  python main.py")
            
            print_info("\nCommand-Line Mode:")
            print("  python main.py embed <image> <payload> <output> [--password <pass>] [--no-compress]")
            print("  python main.py extract <image> <output_file> [--password <pass>]")
            print("  python main.py run <code_file>")
            print("  python main.py workflow <image> <payload> [output] [--run] [--password <pass>]")
            
            print_info("\nPayload Management:")
            print("  python main.py payload list")
            print("  python main.py payload add <file> [name]")
            print("  python main.py payload view <name>")
            
            print_info("\nConfiguration:")
            print("  python main.py config")
            print("  python main.py config set <key> <value>")
            
            print_info("\nExamples:")
            print("  python main.py workflow input.png malware.py output.png --run")
            print("  python main.py embed cover.png payload.py stego.png --password secret123")
            print("  python main.py payload add keylogger.py")
            print("  python main.py config set encryption_enabled true")
            
        else:
            print_error(f"Unknown command: {command}")
            print_info("Run 'python main.py help' for usage information")
            sys.exit(1)
            
    except Exception as e:
        print_error(f"Operation failed: {e}")
        sys.exit(1)