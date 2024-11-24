import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

def compress_image(input_array, initial_block_size, quality):
    height, width, _ = input_array.shape

    # Create output image array
    output_array = np.zeros_like(input_array)

    # Process in blocks
    for y in range(0, height, initial_block_size):
        for x in range(0, width, initial_block_size):
            # Get block
            block = get_block(input_array, x, y, initial_block_size)

            # Analyze similarity between blocks and adjust compression strength
            adaptive_block_size = adjust_block_size(block, initial_block_size, quality)

            # Get new block
            adjusted_block = get_block(input_array, x, y, adaptive_block_size)

            # Compress block
            compressed_block = compress_block_with_quality(adjusted_block, quality)

            # Apply compressed block to output image
            set_block(output_array, x, y, compressed_block, adaptive_block_size)

    # Return output image
    return output_array

# Get block
def get_block(image_array, start_x, start_y, block_size):
    height, width, _ = image_array.shape
    end_x = min(start_x + block_size, width)
    end_y = min(start_y + block_size, height)
    block = image_array[start_y:end_y, start_x:end_x]
    return block

# Adjust block size (analyze similarity between blocks)
def adjust_block_size(block, block_size, quality):
    h, w, _ = block.shape
    pixel_count = h * w
    sum_diff = 0

    # Calculate RGB differences within the block
    for y in range(h - 1):
        for x in range(w - 1):
            rgb1 = block[y, x]
            rgb2 = block[y, x + 1]
            rgb3 = block[y + 1, x]

            # Color difference
            sum_diff += color_difference(rgb1, rgb2) + color_difference(rgb1, rgb3)

    avg_diff = sum_diff / pixel_count

    # Determine block size based on quality
    if avg_diff < (50 * quality):
        return min(block_size * 2, 32)  # Increase block size if similar
    return block_size

# Compress block (based on quality)
def compress_block_with_quality(block, quality):
    h, w, _ = block.shape
    pixel_count = h * w

    # Calculate average color
    avg_color = block.mean(axis=(0, 1))

    # Adjust color based on quality
    compressed_block = np.zeros_like(block)
    for y in range(h):
        for x in range(w):
            compressed_block[y, x] = ((1 - quality) * avg_color + quality * block[y, x]).astype(int)
    return compressed_block

# Calculate color difference
def color_difference(rgb1, rgb2):
    return np.sum(np.abs(rgb1 - rgb2))

# Set block
def set_block(output_array, start_x, start_y, block, block_size):
    h, w, _ = block.shape
    output_array[start_y:start_y + h, start_x:start_x + w] = block

# UI implementation
class UI:
    # Constructor implementation
    def __init__(self, main):
        self.main = main
        main.title("Image Compressor")  # Window title

        # Button to load an image from a desired location
        self.load_button = tk.Button(main, text="Load Image", command=self.load_image)  # command: Specify callback function
        self.load_button.pack(pady=5)     # pack: Place widget on main

        # Button to save the compressed image to a desired location
        self.save_button = tk.Button(main, text="Save Compressed Image", command=self.save_compressed_image)
        self.save_button.pack(pady=5)

        # Space to display preview images
        self.canvas = tk.Canvas(main, width=850, height=450)
        self.canvas.pack()

        self.original_image = None      # Original image
        self.compressed_image = None    # Compressed image

    # Load image
    def load_image(self):
        file_path = filedialog.askopenfilename()  # Access user's storage to read the file
        if file_path:   # If the file path is valid
            self.original_image = np.array(Image.open(file_path).convert('RGB'))  # Convert to numpy format before passing to compress_image function
            self.update_compression()

    # Proceed with compression
    def update_compression(self):
        if self.original_image is not None:
            initial_block_size = 8  # Initial block size
            quality = 0.5           # Compression quality (0.0 ~ 1.0)
            self.compressed_image = compress_image(self.original_image, initial_block_size, quality)  # Get compressed image
            self.display_images()

    # Preview images
    def display_images(self):
        height, width, _ = self.original_image.shape  # Get size of original image

        # Resize images
        min_dimension = min(width, height)             # Minimum of width and height dimensions
        ratio = 290 / min_dimension                     # Resize factor
        new_height, new_width = int(height * ratio), int(width * ratio)  # Resizing

        # Process images for previewing
        original_resized = Image.fromarray(self.original_image).resize((new_width, new_height), Image.LANCZOS)
        compressed_resized = Image.fromarray(self.compressed_image).resize((new_width, new_height), Image.LANCZOS)
        self.original_photo = ImageTk.PhotoImage(image=original_resized)
        self.compressed_photo = ImageTk.PhotoImage(image=compressed_resized)

        self.canvas.delete("all")   # Clear canvas

        # Display preview images
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.original_photo)
        self.canvas.create_image(new_width + 10, 0, anchor=tk.NW, image=self.compressed_photo)

        # Description text for images (at the bottom)
        self.canvas.create_text(new_width // 2, new_height + 20, text="Original Image")
        self.canvas.create_text(new_width + new_width // 2 + 10, new_height + 20, text="Compressed Image")

    # Save compressed image
    def save_compressed_image(self):
        if self.compressed_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpeg",
                                                     # Extension (default: jpeg)
                                                     filetypes=[("JPEG files", "*.jpeg"),
                                                                ("PNG files", "*.png"),
                                                                ("JPG files", "*.jpg")
                                                                ])
            # When an image has been loaded
            if file_path:
                Image.fromarray(self.compressed_image).save(file_path)  # Save the image
                messagebox.showinfo("Save", "Image successfully saved!")

        # When the image has not been loaded yet
        else:
            messagebox.showwarning("Save", "Please compress an image first!")

# Activate UI
root = tk.Tk()
app = UI(root)
root.mainloop()