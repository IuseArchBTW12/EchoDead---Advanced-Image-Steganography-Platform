#!/usr/bin/env python3
"""
Payload Obfuscation Module
Advanced code obfuscation techniques to evade detection
"""

import base64
import random
import string
import zlib
import ast
import re
from typing import Optional


class PayloadObfuscator:
    """
    Advanced payload obfuscation using multiple techniques:
    - Variable name randomization
    - String encryption
    - Dead code injection
    - Control flow flattening
    - Base64 layering
    """
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize obfuscator with optional random seed"""
        self.seed = seed
        if seed:
            random.seed(seed)
    
    def generate_random_name(self, length: int = 8) -> str:
        """Generate random variable name"""
        first_char = random.choice(string.ascii_lowercase)
        rest = ''.join(random.choices(string.ascii_lowercase + string.digits + '_', k=length-1))
        return first_char + rest
    
    def obfuscate_strings(self, code: str) -> str:
        """
        Encrypt all string literals in the code
        Replaces "string" with base64.b64decode(...).decode()
        """
        def replace_string(match):
            original_string = match.group(1)
            # Skip very short strings and special strings
            if len(original_string) < 3 or original_string in ['r', 'n', 't', 'b']:
                return match.group(0)
            
            # Encode string
            encoded = base64.b64encode(original_string.encode()).decode()
            var_name = self.generate_random_name()
            return f'__import__("base64").b64decode("{encoded}").decode()'
        
        # Match strings in quotes (both single and double)
        code = re.sub(r'"([^"]+)"', replace_string, code)
        code = re.sub(r"'([^']+)'", replace_string, code)
        
        return code
    
    def randomize_variable_names(self, code: str) -> str:
        """
        Randomize all variable names while preserving functionality
        This is a simplified version - full implementation would use AST
        """
        # Common variable patterns to obfuscate
        common_vars = ['data', 'result', 'response', 'output', 'temp', 'value', 
                      'info', 'content', 'text', 'payload', 'config']
        
        var_map = {}
        for var in common_vars:
            new_name = self.generate_random_name(10)
            var_map[var] = new_name
        
        # Replace variables (word boundaries to avoid partial matches)
        for old_var, new_var in var_map.items():
            code = re.sub(rf'\b{old_var}\b', new_var, code)
        
        return code
    
    def inject_dead_code(self, code: str, num_injections: int = 5) -> str:
        """
        Inject useless but syntactically correct code to confuse analysis
        """
        dead_code_templates = [
            "if False: {var1} = {value}",
            "{var1} = {value} if {var2} < 0 else {var1}",
            "_ = [{value}, {value}, {value}]",
            "pass  # {comment}",
            "{var1} = str({value}) if False else {var1}",
        ]
        
        lines = code.split('\n')
        insertion_points = random.sample(range(len(lines)), min(num_injections, len(lines)))
        
        for point in sorted(insertion_points, reverse=True):
            template = random.choice(dead_code_templates)
            dead_line = template.format(
                var1=self.generate_random_name(),
                var2=self.generate_random_name(),
                value=random.randint(1, 999),
                comment=''.join(random.choices(string.ascii_letters, k=20))
            )
            # Match indentation
            indent = len(lines[point]) - len(lines[point].lstrip())
            lines.insert(point + 1, ' ' * indent + dead_line)
        
        return '\n'.join(lines)
    
    def add_polymorphic_wrapper(self, code: str) -> str:
        """
        Wrap code in polymorphic layer that changes each time
        """
        # Generate random variable names
        exec_var = self.generate_random_name(12)
        decode_var = self.generate_random_name(12)
        compressed_var = self.generate_random_name(12)
        
        # Compress and encode the original code
        compressed = zlib.compress(code.encode(), level=9)
        encoded = base64.b64encode(compressed).decode()
        
        wrapper = f'''# Polymorphic wrapper - generated on {random.randint(1000000, 9999999)}
import base64, zlib
{compressed_var} = "{encoded}"
{decode_var} = lambda x: zlib.decompress(base64.b64decode(x))
{exec_var} = {decode_var}({compressed_var}).decode()
exec({exec_var})
'''
        return wrapper
    
    def obfuscate_imports(self, code: str) -> str:
        """
        Obfuscate import statements using __import__()
        """
        def replace_import(match):
            module = match.group(1)
            var_name = self.generate_random_name()
            return f'{var_name} = __import__("{module}")'
        
        # Replace "import module"
        code = re.sub(r'^import\s+(\w+)', replace_import, code, flags=re.MULTILINE)
        
        return code
    
    def full_obfuscation(self, code: str, level: str = 'medium') -> str:
        """
        Apply full obfuscation pipeline
        
        Levels:
        - light: Basic string encoding
        - medium: Strings + variable names + dead code
        - heavy: All techniques + polymorphic wrapper
        """
        if level == 'light':
            code = self.obfuscate_strings(code)
        
        elif level == 'medium':
            code = self.obfuscate_strings(code)
            code = self.randomize_variable_names(code)
            code = self.inject_dead_code(code, num_injections=3)
        
        elif level == 'heavy':
            code = self.obfuscate_strings(code)
            code = self.randomize_variable_names(code)
            code = self.inject_dead_code(code, num_injections=8)
            code = self.obfuscate_imports(code)
            code = self.add_polymorphic_wrapper(code)
        
        return code


def test_obfuscation():
    """Test obfuscation on sample code"""
    sample_code = '''
import os
import sys

def get_system_info():
    hostname = os.environ.get("COMPUTERNAME", "Unknown")
    username = os.environ.get("USERNAME", "Unknown")
    data = f"Host: {hostname}, User: {username}"
    return data

result = get_system_info()
print(result)
'''
    
    obfuscator = PayloadObfuscator()
    
    print("=" * 60)
    print("ORIGINAL CODE:")
    print("=" * 60)
    print(sample_code)
    
    print("\n" + "=" * 60)
    print("LIGHT OBFUSCATION (String Encoding):")
    print("=" * 60)
    print(obfuscator.full_obfuscation(sample_code, level='light'))
    
    print("\n" + "=" * 60)
    print("MEDIUM OBFUSCATION (Strings + Variables + Dead Code):")
    print("=" * 60)
    print(obfuscator.full_obfuscation(sample_code, level='medium'))
    
    print("\n" + "=" * 60)
    print("HEAVY OBFUSCATION (Full Polymorphic):")
    print("=" * 60)
    print(obfuscator.full_obfuscation(sample_code, level='heavy'))


if __name__ == '__main__':
    test_obfuscation()
