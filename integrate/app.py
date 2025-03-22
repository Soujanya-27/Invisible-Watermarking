from flask import Flask, request, send_file, render_template, url_for
import cv2
import numpy as np
import io
import random
import recover_watermark  # Import the recovery module
import os

app = Flask(__name__)

def embed_watermark_lsb(image_data, watermark_text):
    """Embeds a text watermark into an image using LSB."""
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to load image.")

    original_height, original_width = image.shape[:2]

    binary_watermark = ''.join(format(ord(char), '08b') for char in watermark_text)
    binary_watermark_length = len(binary_watermark).to_bytes(4, 'big') #add length indicator.
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

def recover_watermark_lsb_in_memory(image):
    """Recovers a watermark from an image in memory using LSB."""
    pixels = image.reshape((-1, 3))
    random.seed(42)  # Use the same seed as in embedding

    # Recover the length of the watermark
    binary_message_length_bits = ""
    indices_length = random.sample(range(pixels.shape[0]), 32)
    for i in range(32):
        pixel_index = indices_length[i]
        channel = i % 3
        binary_message_length_bits += str(pixels[pixel_index, channel] & 1)

    message_length_bytes = int(binary_message_length_bits, 2).to_bytes(4, 'big')
    message_length = int.from_bytes(message_length_bytes, 'big')

    # Recover the actual watermark
    binary_message = ""
    indices_message = random.sample(range(pixels.shape[0]), message_length * 8)
    for i in range(message_length * 8):
        pixel_index = indices_message[i]
        channel = i % 3
        binary_message += str(pixels[pixel_index, channel] & 1)

    # Convert binary message to text
    message_bytes = int(binary_message, 2).to_bytes(message_length, 'big')
    message = message_bytes.decode('utf-8', errors='ignore')

    return message
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return 'No image file provided', 400
        image_file = request.files['image']
        action = request.form.get('action')

        if action == 'recover':
            try:
                image_data = image_file.read()
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if image is None:
                    return "Invalid image", 400
                recovered_message = recover_watermark_lsb_in_memory(image) # Corrected call # changed to in memory function.
                return render_template('index.html', recovered_message=recovered_message)
            except ValueError as e:
                return str(e), 400
            except Exception as e:
                return f"An error occurred: {str(e)}", 500

        elif action == 'embed':
            watermark_text = request.form.get('text', 'WATERMARK')
            try:
                image_data = image_file.read()
                watermarked_image = embed_watermark_lsb(image_data, watermark_text)
                is_success, buffer = cv2.imencode(".png", watermarked_image)
                if not is_success:
                    return "Failed to encode image", 500
                io_buf = io.BytesIO(buffer)
                return send_file(io_buf, mimetype='image/png', as_attachment=True, download_name='watermarked.png')
            except ValueError as e:
                return str(e), 400
            except cv2.error as e:
                return f"OpenCV error: {str(e)}", 500
            except Exception as e:
                return f"An unexpected error occurred: {str(e)}", 500

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)