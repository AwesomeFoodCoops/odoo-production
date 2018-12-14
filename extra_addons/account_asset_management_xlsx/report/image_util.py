# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)

from openerp.tools import image as IMG
import base64
import os
import logging
import tempfile
_logger = logging.getLogger(__name__)


def get_record_image_path(record, image, size=(128, 128)):
    """
    :param record: instance of model
    :param image: example: product_id.image
    :param size: example: (128, 128)
    :return: path to image or None if no image
    """
    if not image:
        return None

    temp_folder = tempfile.mkdtemp()
    record_image_path = os.path.join(
        temp_folder, str(record.id) + ".jpg")
    try:
        record_image = IMG.image_resize_image(
            image, size)
        record_image = base64.b64decode(record_image)
        with open(record_image_path, 'wb') as f:
            f.write(record_image)
            return record_image_path
    except Exception as e:
        logging.error('Error when processing the image for'
                      'record: %s: %s', record, str(e))
        raise e
    return False
