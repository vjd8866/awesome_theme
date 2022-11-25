# -*- coding: utf-8 -*-

from math import fabs
from odoo import exceptions

def apply_alpha(var_name, color, alpha, color_type = False):
    """
    safe alpha
    :param color:
    :param alpha:
    :return:
    """
    if not color:
        return ''
        
    # check var_name endwith text_color
    if var_name.endswith("text_color") or color_type == "text_color":
        return color

    # replace white to fff and black to 000 etc
    if color == "white":
        color = "fff"
    elif color == "black":
        color = "000"
    elif color == "red":
        color = "f00"
    elif color == "green":
        color = "0f0"
    elif color == "blue":
        color = "00f"
    elif color == "yellow":
        color = "ff0"

    # check if start with rgba
    if color.startswith("rgba"):
        # get the content between ( and )
        color = color[color.find("(") + 1:color.find(")")]
        # get the alpha
        rgba_color = color.split(",")
        if len(rgba_color) == 4:
            # convert to float
            tmp = float(rgba_color[3])
            # check var_name has shadow in it
            tmp = alpha * tmp
            # make rgba string
            tmp = "rgba({rgba_color[0]},{rgba_color[1]},{rgba_color[2]},{tmp})".format(
                rgba_color=rgba_color,
                tmp=tmp)
            return tmp
        else:
            return color
    # check if start with # and length is 9
    elif color.startswith("#"):
        if len(color) == 9 or len(color) == 7:
            # get red color
            red = color[1:3]
            # get green color
            green = color[3:5]
            # get blue color
            blue = color[5:7]
            # get the old alpha
            if len(color) == 9:
                old_alpha = color[7:9]
                # convert to int
                old_alpha = int(old_alpha, 16) / 255
                new_alpha = int(old_alpha * alpha)
            else:
                new_alpha = alpha

            # make rgba string
            return "rgba({red},{green},{blue},{new_alpha})".format(
                red=int(red, 16),
                green=int(green, 16),
                blue=int(blue, 16),
                new_alpha=new_alpha)
        # color like #ffff
        elif len(color) == 5:
            # get red color
            red = color[1:2]
            # get green color
            green = color[2:3]
            # get blue color
            blue = color[3:4]
            # alpha
            old_alpha = color[4:5]
            # convert to int
            old_alpha = int(old_alpha + old_alpha, 16) / 255
            new_alpha = old_alpha * alpha
            
            # make rgba string
            return "rgba({red},{green},{blue},{alpha})".format(
                red=int(red + red, 16),
                green=int(green + green, 16),
                blue=int(blue + blue, 16),
                alpha=new_alpha)
                  
        # color like #fff
        elif len(color) == 4:
            # get red color
            red = color[1:2]
            # get green color
            green = color[2:3]
            # get blue color
            blue = color[3:4]
            # make rgba string
            return "rgba({red},{green},{blue},{alpha})".format(
                red=int(red + red, 16),
                green=int(green +green, 16),
                blue=int(blue + blue, 16),
                alpha=alpha)
        else:
            return color
    else:
        # check if start with rgb
        if color.startswith("rgb"):
            # get the content between ( and )
            color = color[color.find("(") + 1:color.find(")")]
            # get the alpha
            rgb_color = color.split(",")
            if len(rgb_color) == 3:
                # make rgba string
                tmp = "rgba({rgb_color[0]},{rgb_color[1]},{rgb_color[2]},{alpha})".format(
                    rgb_color=rgb_color,
                    alpha=alpha)
                return tmp
            else:
                return color
        else:
            return 'rgba({color},{alpha})'.format(color=color, alpha=alpha)

def split_module_and_path(file_path):
    """
    get module from path
    :param file_path:
    :return:
    """
    # lstrip '/' and '\\'
    file_path = file_path.lstrip('/').lstrip('\\')
    module_path = file_path.split("/", 1)
    if len(module_path) != 2:
        raise exceptions.ValidationError('path is not valid! {}'.format(file_path))

    if len(module_path) > 1:
        module = module_path[0]
        file_path = module_path[1]
        return module, file_path
    else:
        return None, None
