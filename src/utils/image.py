import os
from PIL import Image, ImageTk

def load_and_scale_image(path, size):
    """
    Loads an image from a given path, scales it to the specified size (width, height),
    and returns a Tkinter-compatible PhotoImage.
    
    If the image does not exist, a transparent fallback image is returned.
    """
    if not os.path.exists(path):
        # Create a transparent fallback of the specified size
        fallback = Image.new("RGBA", size, (255, 255, 255, 0))
        return ImageTk.PhotoImage(fallback)
        
    try:
        img = Image.open(path)
        # Use Image.Resampling.LANCZOS (Pillow 10+) or fallback to LANCZOS
        try:
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resample_filter = Image.LANCZOS
            
        scaled_img = img.resize(size, resample_filter)
        return ImageTk.PhotoImage(scaled_img)
    except Exception as e:
        print(f"Error loading image at {path}: {e}")
        fallback = Image.new("RGBA", size, (255, 255, 255, 0))
        return ImageTk.PhotoImage(fallback)
