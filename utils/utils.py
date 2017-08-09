"""
Utils.py: provides some utility methods that are commonly called.
"""
import time
import uuid
from cv2 import imdecode, imencode, IMWRITE_PNG_COMPRESSION, IMWRITE_JPEG_QUALITY
import copy

import google.protobuf
import numpy as np

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '0.1'
__maintainer__ = 'Curtis West'
__email__ = "curtis@curtiswest.net"
__status__ = 'Development'


def unwrap_to_list(item):
    """
    Takes a Protobuf's RepeatedScalarFieldContainer and converts it into its native Python list type, if needed, else
    returns the item in a list.
    Args:
        item: the item to be unwrapped in a list
    Returns:
        list: the item unwrapped appropriately wrap in a list in native Python types
    """
    if isinstance(item, google.protobuf.internal.containers.RepeatedScalarFieldContainer):
        if len(item) > 0:
            conv_type = int if isinstance(item[0], int) else float if isinstance(item[0], float) else str
            return [conv_type(i) for i in item]
        else:
            return None
    elif isinstance(item, list):
        return item
    else:
        return [item]


def wrap_to_list(items):
    """
    Returns the item guaranteed to be wrap in a list while not affecting raw strings, or double wrapping lists.
    Args:
        items: the item to be wrap in a list

    Returns:
        list: the item wrap appropriately wrap in a list
    """
    if isinstance(items, list):
        return items
    elif isinstance(items, tuple):
        return list(items)
    else:
        return [items]


def encode_image(image, compressed=True, level=90):
    """
    Encodes an OpenCV2 `image` (usually a BGR-array) either compressed or uncompressed.
    Args:
        image: an OpenCV2 image (usually a BGR array) representing the image to compress
        compressed: true for JPEG compression, false for PNG lossless compression
        level: the level to compress at.
        0 (lowest quality) to 100 (highest quality) for JPEG compression (i.e. `compressed = True`)
        0 (quickest, larger file size) to 9 (slower, smaller file size) for PNG compression (i.e. `compressed = False`)
    Returns:
        str: the image encoded into a string
    """
    if compressed:
        _, image_data = imencode('.jpg', image, [IMWRITE_JPEG_QUALITY, level])
    else:
        _, image_data = imencode('.png', image, [IMWRITE_PNG_COMPRESSION, level])
    return image_data.flatten().tostring()


def decode_image(image_data_str):
    """
    Decodes an image from the given string into a BGR array.
    Args:
        image_data_str: the string holding an image to be decoded
    Returns:
        list: the decoded image in OpenCV2 image format.
    """
    return imdecode(np.fromstring(image_data_str, dtype='uint8'), 1)


def variables_in_class(cls):
    """
    Returns all the defined variables stored in a class, excluding set variables such as __init__, __dict__ etc.
    Args:
        cls: the class to retrieve variables from
    Returns:
        dict: dictionary with key containing the variable name and value being the key variable's value
    """
    var_dict = dict((vars(cls)))
    known_keys = ['__module__', '__doc__', '__init__', '__dict__']
    for key in known_keys:
        if key in var_dict:
            del var_dict[key]
    return var_dict


def in_out(input_str, output_str):
    """
    Formats the input_str, output_str for printing.

    Examples:
        >>> print in_out('Expected Input', 'Actual Output')
        In : Expected Input
        Out: Actual Output

    Args:
        input_str: the expected input string
        output_str: the actual output string

    Returns:
        str: the formatted in/out string
    """
    return '\nIn : {} \nOut: {}'.format(input_str, output_str)


def generate_id(num_digits=4):
    """
    Generates a num_digits long unique hexadecimal ID, based on a UUID
    """
    return uuid.uuid4().hex[-num_digits:]


def generate_random_img():
    """
    Generates a random RGB image list.
    Returns:
        list: the RGB image
    """
    return np.random.rand(1920, 1080, 3) * 255


def iterify(iterable):
    """
    Converts a string or list of strings into an iterable object without iterating over the letters in the strings.

    Author: @kindall on StackOverflow (https://stackoverflow.com/a/6710895/8144376)
    """
    if isinstance(iterable, basestring):
        iterable = [iterable]
    try:
        iter(iterable)
    except TypeError:
        iterable = [iterable]
    return iterable
