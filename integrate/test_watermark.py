import cv2
import numpy as np
import random
import os

def embed_watermark_lsb(image_data, watermark_text):
    """Embeds a text watermark into an image using LSB with length indicator."""
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to load image.")

    original_height, original_width = image.shape[:2]

    binary_watermark = ''.join(format(ord(char), '08b') for char in watermark_text)
    binary_watermark_length = len(binary_watermark).to_bytes(4, 'big')
    binary_watermark_length_bits = ''.join(format(byte, '08b') for byte in binary_watermark_length)
    binary_watermark = binary_watermark_length_bits + binary_watermark

    binary_watermark = [int(bit) for bit in binary_watermark]

    if len(binary_watermark) > image.size:
        raise ValueError("Watermark too large for image.")

    pixels = image.reshape((-1, 3))
    random.seed(42)
    indices = random.sample(range(pixels.shape[0]), len(binary_watermark))

    for i, bit in enumerate(binary_watermark):
        pixel_index = indices[i]
        channel = i % 3
        original_pixel = pixels[pixel_index, channel]
        modified_pixel = (int(original_pixel) & ~1) | bit
        pixels[pixel_index, channel] = np.uint8(modified_pixel)

    watermarked_image = pixels.reshape((original_height, original_width, 3))
    return watermarked_image

def recover_watermark_lsb(image_path):
    """Recovers a text watermark from an LSB-watermarked image with length indicator."""
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
    print(f"watermark_length_bits (hex): {hex(int(watermark_length_bits, 2))}") #Debugging
    watermark_length = int.from_bytes(int(watermark_length_bits, 2).to_bytes(4, 'big'), 'big')
    print(f"watermark_length: {watermark_length}")
    print(f"Length of binary_string: {len(binary_string)}") #debugging
    binary_string = binary_string[32: 32 + watermark_length]
    print(f"truncated binary string: {binary_string}")

    text_watermark = ''
    try:
        for i in range(0, len(binary_string), 8):
            iteration_count += 1
            if iteration_count > max_iterations:
                print("Loop exceeded maximum iterations.")
                break
            byte = binary_string[i:i + 8]
            if len(byte) == 8:
                text_watermark += chr(int(byte, 2))
            else:
                break
    except ValueError as e:
        print(f"Error decoding: {e}")

    return text_watermark

# Test with a simple image and watermark
image_path = "output/input_image.jpg"  # Replace with a path to your image
watermark_text = "test"

# Embed
test_image = cv2.imread(image_path)
if test_image is None:
    print("Error loading test image")
else:
    watermarked_image = embed_watermark_lsb(cv2.imencode(".png", test_image)[1].tobytes(), watermark_text)
    cv2.imwrite("watermarked_test.png", watermarked_image)

# Recover
recovered_message = recover_watermark_lsb("watermarked_test.png")
print(f"Recovered message: {recovered_message}")
os.remove("watermarked_test.png")