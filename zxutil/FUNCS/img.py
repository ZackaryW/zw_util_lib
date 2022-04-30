import typing
from zxutil.FUNCS import parse_dimension_string
from PIL import Image

def combine_linear_image(dimension :str,*args):
    if len(args) == 0:
        return None
    
    val = parse_dimension_string(dimension)

    if val is None:
        raise ValueError("invalid dimension string")

    x, y = val

    if x == 0 or y == 0:
        raise ValueError("invalid dimension string")

    if len(args) == 1:
        raise ValueError("invalid number of arguments")

    args_num = len(args)

    width = x * args_num
    height = y

    img = Image.new("RGBA", (width, height))
    pend_name = ""
    for i, arg in enumerate(args):
        if not isinstance(arg, typing.Iterable):
            raise ValueError("invalid argument")
        if not len(arg) == 2:
            raise ValueError("invalid iterable length")

        arg_img = arg[0]
        arg_name = arg[1]
        
        if arg is None:
            pend_name += "0."
            continue
        img.paste(arg_img, (i * x, 0))
        pend_name += arg_name + "."
    
    return img, pend_name[:-1]