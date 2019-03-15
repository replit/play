color_names = {
    'black':        (  0,   0,   0),
    'white':        (255, 255, 255),
    'red':          (255,   0,   0),
    'green':        (0  , 255,   0),
    'blue':         (0  ,   0, 255),
}

def color_name_to_rgb(name):
    if type(name) == tuple:
        return name

    try:
        return color_names[name.lower().strip()]
    except KeyError:
        raise Exception(f"""

You gave a color name we don't understand: '{name}'
If this our mistake, please let us know. Otherwise, try using the RGB number form of the color e.g. '(0, 255, 255)'.
You can find the color form of a color on websites like this: https://www.rapidtables.com/web/color/RGB_Color.html\n""")