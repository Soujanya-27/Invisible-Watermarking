import cv2
import numpy as np
import random

def recover_watermark_lsb(image_path):
    """Recovers a text watermark from an LSB-watermarked image."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Unable to load image.")

    pixels = image.reshape((-1, 3))
    random.seed(42)
    indices = random.sample(range(pixels.shape[0]), len(pixels))

    binary_watermark = []
    for i in indices:
        if len(binary_watermark) >= len(pixels):
            break
        binary_watermark.append(pixels[i % len(indices), i % 3] & 1)

    binary_string = ''.join(str(bit) for bit in binary_watermark)
    print(f"Binary string: {binary_string}")
    watermark_length_bits = binary_string[:32]
    print(f"watermark_length_bits: {watermark_length_bits}")
    watermark_length = int.from_bytes(int(watermark_length_bits, 2).to_bytes(4, 'big'), 'big')
    print(f"watermark_length: {watermark_length}")
    binary_string = binary_string[32: 32 + watermark_length]
    print(f"truncated binary string: {binary_string}")
    text_watermark = ''
    try:
        for i in range(0, len(binary_string), 8):
            byte = binary_string[i:i + 8]
            if len(byte) == 8:
                text_watermark += chr(int(byte, 2))
            else:
                break
    except ValueError as e:
        print(f"Error decoding: {e}")

    return text_watermark