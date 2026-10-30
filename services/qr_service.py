"""
RecycleTrace - QR Code Service
Generates batch QR codes linking to the public tracking page.
"""
import io
import os
import qrcode
from qrcode.image.pure import PyPNGImage
import logging

logger = logging.getLogger(__name__)


def generate_batch_qr(batch_id: str, base_url: str) -> bytes:
    """
    Generate a PNG QR code linking to the public batch tracking page.
    Returns raw PNG bytes.
    """
    tracking_url = f"{base_url.rstrip('/')}/track/{batch_id}"

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(tracking_url)
    qr.make(fit=True)

    try:
        # Try using PIL
        from PIL import Image
        img = qr.make_image(fill_color="#1a5c2e", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        # Fallback to pure PNG
        img = qr.make_image(image_factory=PyPNGImage)
        buf = io.BytesIO()
        img.save(buf)
        return buf.getvalue()


def save_batch_qr(batch_id: str, base_url: str, upload_folder: str) -> str:
    """
    Generate and save QR code to disk.
    Returns the relative file path.
    """
    qr_dir = os.path.join(upload_folder, "qrcodes")
    os.makedirs(qr_dir, exist_ok=True)

    filename = f"{batch_id}.png"
    filepath = os.path.join(qr_dir, filename)

    png_bytes = generate_batch_qr(batch_id, base_url)
    with open(filepath, "wb") as f:
        f.write(png_bytes)

    return os.path.join("qrcodes", filename)
