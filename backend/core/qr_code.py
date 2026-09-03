import segno
from PIL import Image, ImageFile
from io import BytesIO
import base64

from ..models.ticket_models import Ticket

# TODO: Add to `config.ini` or other config location in some way
_qr_params = {
    'scale': 10
}

def encode_uuid_utf(uuid_bytes: bytes) -> str:
    return base64.b64encode(uuid_bytes).decode('utf-8')

def get_qr_from_value(ticket: Ticket | list[Ticket]) -> BytesIO:
    qr = segno.make_qr(ticket.qr_value)
    # qr = segno.make_qr("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # Rick Roll someone

    buffer = BytesIO()
    qr.save(buffer, kind="png", **_qr_params)
    buffer.seek(0)  # Reset stream position back to beginning after saving
    return buffer

def generate_qr_buffer(ticket: list[Ticket]) -> BytesIO:
    buffer_list = [get_qr_from_value(t) for t in ticket]
    if len(buffer_list) > 1:  # If we have more than one element, do some processing to append
        img_list: list[ImageFile.ImageFile] = []
        '''Use `Pillow.Image` to append values together in `BytesIO`
        would probably (technically) be more efficient to just 
        write to the the buffer directly but whatever 
        (would have to deal with buffer size stuff then)
        '''
        for qr in buffer_list:  
            img = Image.open(qr)
            img_list.append(img)

        if img_list:  # Safety
            buffer = BytesIO()
            im = img_list.pop(0)  # Remove and get first index of list for saving
            im.save(buffer, format="pdf", save_all=True, append_images=img_list)
            buffer.seek(0)  # Reset stream position back to beginning after saving
            return buffer

    # If we only have one element in the list (i.e. only 1 ticket)
    return buffer_list[0]