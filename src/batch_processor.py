#!/usr/bin/env python3
"""
Batch Processing Module
Embed payloads in multiple images simultaneously for mass distribution
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import random
import string
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# We'll define our own simplified embed function since main.py has complex dependencies
def _embed_payload(image_path: str, payload_path: str, output_path: str, password: Optional[str] = None) -> bool:
    """
    Simplified embedding function for batch operations
    Uses LSB steganography to embed payload in image
    """
    try:
        from PIL import Image
        import numpy as np
        
        # Read payload
        with open(payload_path, 'rb') as f:
            payload = f.read()
        
        # Convert to binary
        payload_binary = ''.join(format(byte, '08b') for byte in payload)
        payload_length = len(payload)
        
        # Load image
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Flatten image array
        flat = img_array.flatten()
        
        # Check if payload fits
        if len(payload_binary) + 32 > len(flat):
            return False
        
        # Embed payload length (first 32 bits)
        length_binary = format(payload_length, '032b')
        for i in range(32):
            flat[i] = (flat[i] & 0xFE) | int(length_binary[i])
        
        # Embed payload
        for i, bit in enumerate(payload_binary):
            flat[32 + i] = (flat[32 + i] & 0xFE) | int(bit)
        
        # Reshape and save
        embedded_array = flat.reshape(img_array.shape)
        embedded_img = Image.fromarray(embedded_array.astype(np.uint8))
        embedded_img.save(output_path)
        
        return True
    except Exception as e:
        print(f"Error embedding: {e}")
        return False


class BatchProcessor:
    """
    Mass embedding operations for distributing payloads at scale
    """
    
    def __init__(self, max_workers: int = 4):
        """Initialize with thread pool size"""
        self.max_workers = max_workers
        self.results: List[Dict] = []
    
    def generate_random_filename(self, extension: str = '.png', length: int = 12) -> str:
        """Generate random filename for stealth"""
        chars = string.ascii_letters + string.digits
        name = ''.join(random.choices(chars, k=length))
        return f"{name}{extension}"
    
    def batch_embed(
        self,
        cover_images: List[str],
        payload_path: str,
        output_dir: str,
        password: Optional[str] = None,
        randomize_names: bool = True,
        use_compression: bool = True
    ) -> Dict[str, any]:
        """
        Embed same payload into multiple images
        
        Args:
            cover_images: List of cover image paths
            payload_path: Path to payload to embed
            output_dir: Directory for output images
            password: Optional encryption password
            randomize_names: Generate random output filenames
            use_compression: Use compression
        
        Returns:
            Summary dict with results
        """
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Read payload once
        with open(payload_path, 'rb') as f:
            payload_data = f.read()
        
        print(f"📦 Batch Embedding: {len(cover_images)} images")
        print(f"   Payload: {payload_path} ({len(payload_data)} bytes)")
        print(f"   Output: {output_dir}")
        print(f"   Workers: {self.max_workers}")
        print()
        
        results = {
            'total': len(cover_images),
            'successful': 0,
            'failed': 0,
            'details': [],
            'start_time': datetime.now().isoformat(),
        }
        
        def process_image(cover_path: str) -> Tuple[bool, str, Optional[str]]:
            """Process single image (for threading)"""
            try:
                # Generate output filename
                if randomize_names:
                    ext = Path(cover_path).suffix
                    output_name = self.generate_random_filename(extension=ext)
                else:
                    output_name = f"stego_{Path(cover_path).name}"
                
                output_path = os.path.join(output_dir, output_name)
                
                # Embed payload
                embed_payload(
                    cover_path,
                    payload_path,
                    output_path,
                    password=password,
                    use_compression=use_compression
                )
                
                return True, cover_path, output_path
            
            except Exception as e:
                return False, cover_path, str(e)
        
        # Process images in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(process_image, img): img for img in cover_images}
            
            for i, future in enumerate(as_completed(futures), 1):
                success, cover_path, result_or_error = future.result()
                
                if success:
                    results['successful'] += 1
                    status = "✓"
                    results['details'].append({
                        'cover': cover_path,
                        'output': result_or_error,
                        'status': 'success'
                    })
                    print(f"{status} [{i}/{results['total']}] {Path(cover_path).name} → {Path(result_or_error).name}")
                else:
                    results['failed'] += 1
                    status = "✗"
                    results['details'].append({
                        'cover': cover_path,
                        'error': result_or_error,
                        'status': 'failed'
                    })
                    print(f"{status} [{i}/{results['total']}] {Path(cover_path).name} - ERROR: {result_or_error}")
        
        results['end_time'] = datetime.now().isoformat()
        
        # Print summary
        print()
        print("=" * 60)
        print("BATCH EMBEDDING COMPLETE")
        print("=" * 60)
        print(f"✓ Successful: {results['successful']}/{results['total']}")
        print(f"✗ Failed: {results['failed']}/{results['total']}")
        print(f"📁 Output Directory: {output_dir}")
        
        # Save report
        report_path = os.path.join(output_dir, 'batch_report.json')
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📄 Report saved: {report_path}")
        
        return results
    
    def embed_multiple_payloads(
        self,
        cover_images: List[str],
        payloads: List[str],
        output_dir: str,
        password: Optional[str] = None
    ) -> Dict:
        """
        Embed different payloads into different images (1:1 mapping)
        
        Args:
            cover_images: List of cover images
            payloads: List of payloads (must match length of cover_images)
            output_dir: Output directory
            password: Optional password
        
        Returns:
            Results dictionary
        """
        if len(cover_images) != len(payloads):
            raise ValueError(f"Cover images ({len(cover_images)}) and payloads ({len(payloads)}) count mismatch")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"📦 Multiple Payload Embedding: {len(cover_images)} images")
        print(f"   Output: {output_dir}")
        print()
        
        results = {
            'total': len(cover_images),
            'successful': 0,
            'failed': 0,
            'details': [],
            'start_time': datetime.now().isoformat(),
        }
        
        for i, (cover, payload) in enumerate(zip(cover_images, payloads), 1):
            try:
                output_name = f"stego_{i}_{Path(cover).name}"
                output_path = os.path.join(output_dir, output_name)
                
                embed_payload(cover, payload, output_path, password=password)
                
                results['successful'] += 1
                results['details'].append({
                    'cover': cover,
                    'payload': payload,
                    'output': output_path,
                    'status': 'success'
                })
                
                print(f"✓ [{i}/{results['total']}] {Path(cover).name} + {Path(payload).name}")
            
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'cover': cover,
                    'payload': payload,
                    'error': str(e),
                    'status': 'failed'
                })
                print(f"✗ [{i}/{results['total']}] {Path(cover).name} - ERROR: {e}")
        
        results['end_time'] = datetime.now().isoformat()
        
        print()
        print(f"✓ Successful: {results['successful']}/{results['total']}")
        print(f"✗ Failed: {results['failed']}/{results['total']}")
        
        return results
    
    def generate_decoy_images(
        self,
        count: int,
        output_dir: str,
        width: int = 800,
        height: int = 600
    ) -> List[str]:
        """
        Generate random noise images as decoys
        
        Args:
            count: Number of images to generate
            output_dir: Output directory
            width: Image width
            height: Image height
        
        Returns:
            List of generated image paths
        """
        from PIL import Image
        import numpy as np
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        generated = []
        
        print(f"🎨 Generating {count} decoy images ({width}x{height})...")
        
        for i in range(count):
            # Generate random pixel data
            data = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
            img = Image.fromarray(data, 'RGB')
            
            # Save with random name
            filename = self.generate_random_filename(extension='.png')
            filepath = os.path.join(output_dir, filename)
            img.save(filepath)
            
            generated.append(filepath)
            print(f"   ✓ Generated: {filename}")
        
        print(f"✓ {count} decoy images created in {output_dir}")
        
        return generated


def main():
    """Demo batch processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch embed payloads')
    parser.add_argument('--images', nargs='+', required=True, help='Cover images')
    parser.add_argument('--payload', required=True, help='Payload file')
    parser.add_argument('--output', default='batch_output', help='Output directory')
    parser.add_argument('--password', help='Encryption password')
    parser.add_argument('--randomize', action='store_true', help='Randomize output filenames')
    parser.add_argument('--workers', type=int, default=4, help='Number of worker threads')
    
    args = parser.parse_args()
    
    processor = BatchProcessor(max_workers=args.workers)
    processor.batch_embed(
        cover_images=args.images,
        payload_path=args.payload,
        output_dir=args.output,
        password=args.password,
        randomize_names=args.randomize
    )


if __name__ == '__main__':
    main()
