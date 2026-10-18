import base64
from io import BytesIO
from PIL import Image, ImageOps

MAX_DIMENSION = 2048

def process_and_encode_image(bytes_data: bytes) -> str:
    try:
        img = Image.open(BytesIO(bytes_data))
        img.load()
    except Exception as e:
        raise ValueError("Invalid or corrupted image file.") from e
    
    img = ImageOps.exif_transpose(img)

    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.getchannel("A"))
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")
    
    img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
    
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    return f"data:image/JPEG;base64,{b64}"