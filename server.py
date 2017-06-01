import logging
import settings
from io import BytesIO
import textwrap
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, ImageFont, ImageDraw
from flask import abort, Flask, send_file
from structlog import wrap_logger

logging.basicConfig(level=settings.LOGGING_LEVEL,
                    format=settings.LOGGING_FORMAT)
logger = wrap_logger(logging.getLogger(__name__))

app = Flask(__name__)

text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam sit amet scelerisque nulla. Pellentesque mollis tellus ut arcu malesuada auctor. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Ut tristique purus non ultricies vulputate"
text = textwrap.fill(text, 50)

fontcolor = (0, 0, 0)
fontsize = 20
font = ImageFont.truetype('ihatcs.ttf', 40)


class InvalidUsageError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class InMemoryZip(object):
    '''Class for creating in memory Zip objects using BytesIO.'''
    def __init__(self):
        self.in_memory_zip = BytesIO()

    def append(self, filename_in_zip, file_contents):
        '''Appends a file with name filename_in_zip and contents of
        file_contents to the in-memory zip.'''
        # Get a handle to the in-memory zip in append mode
        zf = ZipFile(self.in_memory_zip, "a", ZIP_DEFLATED, False)

        # Write the file to the in-memory zip
        zf.writestr(filename_in_zip, file_contents)
        zf.close()
        return self

    def rewind(self):
        '''Rewinds the read-write position of the in-memory zip to the
        start.'''
        self.in_memory_zip.seek(0)


class InMemoryImage():
    '''Class for creating in memory Pillow Image object using BytesIO.'''
    def __init__(self):
        self.in_memory_image = BytesIO()

    def new_image(self, mode='RGB'):
        '''Creates a new PIL.Image object at self.image.'''
        self.image = Image.new(mode, (6000, 1500), (255, 255, 255))
        draw = ImageDraw.Draw(self.image)
        textsize = draw.textsize(text, font)

        background = (255, 255, 255)
        self.image = Image.new("RGB", textsize, background)
        draw = ImageDraw.Draw(self.image)
        draw.text((0, 0), text, fontcolor, font)
        self.image = self.image.resize((1880, 450), Image.ANTIALIAS)

    def rewind(self):
        '''Rewinds the read-write position of the in-memory zip to the
        start.'''
        self.in_memory_image.seek(0)

    def save_image(self, img_type='JPEG', quality=90):
        '''Saves the image to the BytesIO self.in_memory_image.'''
        self.image.save(self.in_memory_image, img_type, quality=quality)


def stream_image():
    '''Creates an in memory image and streams it back to the caller'''
    in_memory_zip = InMemoryZip()
    in_memory_image = InMemoryImage()

    in_memory_image.new_image()
    in_memory_image.save_image()
    in_memory_image.rewind()

    in_memory_zip.append('image.jpeg', in_memory_image.in_memory_image.read())
    in_memory_zip.rewind()

    return send_file(in_memory_zip.in_memory_zip,
                     attachment_filename='image.zip',
                     mimetype='application/zip')


@app.route('/image')
def serve_image():
    '''Returns an in memory zipfile that contains an image'''
    try:
        return stream_image()
    except Exception:
        abort(500)

if __name__ == '__main__':
    # Startup
    logger.info("Starting server")
    port = settings.PORT
    app.run(debug=True, host='0.0.0.0', port=port)
