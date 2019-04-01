import os as _os
import logging as _logging
import warnings as _warnings
def warning_format(message, category, filename, lineno, file=None, line=None):
    return f'\n{category.__name__}... {message}\n'
_warnings.formatwarning = warning_format


import pygame

import asyncio as _asyncio
import random as _random
import math as _math

from .keypress import pygame_key_to_name as _pygame_key_to_name # don't pollute user-facing namespace with library internals
from .color import color_name_to_rgb as _color_name_to_rgb

def _clamp(num, min_, max_):
    if num < min_:
        return min_
    elif num > max_:
        return max_
    return num

class Oops(Exception):
    def __init__(self, message):
        # for readability, always prepend exception messages in the library with two blank lines
        message = '\n\n\tOops!\n\n\t'+message.replace('\n', '\n\t')+'\n'
        super(Oops, self).__init__(message)

class Hmm(UserWarning):
    pass

pygame.init()

class _screen(object):
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height

    @property 
    def top(self):
        return self.height / 2

    @property 
    def bottom(self):
        return self.height / -2

    @property 
    def left(self):
        return self.width / -2

    @property 
    def right(self):
        return self.width / 2

screen = _screen()

# _pygame_display = pygame.display.set_mode((screen_width, screen_height), pygame.DOUBLEBUF | pygame.OPENGL)
_pygame_display = pygame.display.set_mode((screen.width, screen.height), pygame.DOUBLEBUF)

class _mouse(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self._is_clicked = False
        self._when_clicked_callbacks = []
        self._when_click_released_callbacks = []

    def is_clicked(self):
        return self._is_clicked

    # @decorator
    def when_clicked(self, func):
        async_callback = _make_async(func)
        async def wrapper():
            wrapper.is_running = True
            await async_callback()
            wrapper.is_running = False
        wrapper.is_running = False
        self._when_clicked_callbacks.append(wrapper)
        return wrapper

    # @decorator
    def when_click_released(self, func):
        async_callback = _make_async(func)
        async def wrapper():
            wrapper.is_running = True
            await async_callback()
            wrapper.is_running = False
        wrapper.is_running = False
        self._when_click_released_callbacks.append(wrapper)
        return wrapper

    def distance_to(self, x=None, y=None):
        assert(not x is None)

        try:
            # x can either by a number or a sprite. If it's a sprite:
            x = x.x
            y = x.y
        except AttributeError:
            pass

        dx = self.x - x
        dy = self.y - y

        return _math.sqrt(dx**2 + dy**2)

# @decorator
def when_mouse_clicked(func):
    return mouse.when_clicked(func)
# @decorator
def when_click_released(func):
    return mouse.when_click_released(func)

mouse = _mouse()


all_sprites = []

_debug = True
def debug(on_or_off):
    global _debug
    if on_or_off == 'on':
        _debug = True
    elif on_or_off == 'off':
        _debug = False

background_color = (255, 255, 255)
def set_background_color(color):
    global background_color

    # I chose to make set_background_color a function so that we can give
    # good error messages at the call site if a color isn't recognized.
    # If we didn't have a function and just set background_color like this:
    #
    #       play.background_color = 'gbluereen'
    #
    # then any errors resulting from that statement would appear somewhere
    # deep in this library instead of in the user code.

    if type(color) == tuple:
        background_color = color
    else:
        background_color = _color_name_to_rgb(color)

def random_number(lowest=0, highest=100):
    # if user supplies whole numbers, return whole numbers
    if type(lowest) == int and type(highest) == int:
        return _random.randint(lowest, highest)
    else:
        # if user supplied any floats, return decimals
        return round(_random.uniform(lowest, highest), 2)

def random_color():
    return (random_number(0, 255), random_number(0, 255), random_number(0, 255))


def _raise_on_await_warning(func):
    """
    If someone doesn't put 'await' before functions that require 'await'
    like play.timer() or play.animate(), raise an exception.
    """
    async def f(*args, **kwargs):
        with _warnings.catch_warnings(record=True) as w:
            await func(*args, **kwargs)
            for warning in w:
                str_message = warning.message.args[0] # e.g. "coroutine 'timer' was never awaited"
                if 'was never awaited' in str_message:
                    unawaited_function_name = str_message.split("'")[1]
                    raise Oops(f"""Looks like you forgot to put "await" before play.{unawaited_function_name} on line {warning.lineno} of file {warning.filename}.
To fix this, just add the word 'await' before play.{unawaited_function_name} on line {warning.lineno} of file {warning.filename} in the function {func.__name__}.""")
    return f

def _make_async(func):
    """
    Turn a non-async function into an async function. 
    Used mainly in decorators like @repeat_forever.
    """
    if _asyncio.iscoroutinefunction(func):
        # if it's already async just return it
        return _raise_on_await_warning(func)
    @_raise_on_await_warning
    async def async_func(*args, **kwargs):
        return func(*args, **kwargs)
    return async_func

def new_sprite(image=None, x=0, y=0, size=100, angle=0, transparency=100):
    return sprite(image=image, x=x, y=y, size=size, angle=angle, transparency=transparency)

class sprite(object):
    def __init__(self, image=None, x=0, y=0, size=100, angle=0, transparency=100):
        self._image = image or _os.path.join(_os.path.split(__file__)[0], 'blank_image.png')
        self.x = x
        self.y = y
        self._angle = angle
        self._size = size
        self._transparency = transparency

        self._is_clicked = False
        self._is_hidden = False


        self._compute_primary_surface()

        self._when_clicked_callbacks = []

        all_sprites.append(self)


    def _compute_primary_surface(self):
        try:
            self._primary_pygame_surface = pygame.image.load(_os.path.join(self._image))
        except pygame.error as exc:
            raise Oops(f"""We couldn't find the image file you provided named "{self._image}".
If the file is in a folder, make sure you add the folder name, too.""") from exc
        self._primary_pygame_surface.set_colorkey((255,255,255, 255)) # set background to transparent

        self._should_recompute_primary_surface = False

        # always recompute secondary surface if the primary surface changes
        self._compute_secondary_surface(force=True)

    def _compute_secondary_surface(self, force=False):

        self._secondary_pygame_surface = self._primary_pygame_surface.copy()

        # transparency
        if self._transparency != 100 or force:
            try:
                # for text and images with transparent pixels
                array = pygame.surfarray.pixels_alpha(self._secondary_pygame_surface)
                array[:, :] = (array[:, :] * (self._transparency/100.)).astype(array.dtype) # modify surface pixels in-place
                del array # I think pixels are written when array leaves memory, so delete it explicitly here
            except Exception as e:
                # this works for images without alpha pixels in them
                self._secondary_pygame_surface.set_alpha(round((self._transparency/100.) * 255))

        # scale
        if (self.size != 100) or force:
            ratio = self.size/100.
            self._secondary_pygame_surface = pygame.transform.scale(
                self._secondary_pygame_surface,
                (round(self._secondary_pygame_surface.get_width() * ratio),    # width
                 round(self._secondary_pygame_surface.get_height() * ratio)))  # height


        # rotate
        if (self.angle != 0) or force:
            self._secondary_pygame_surface = pygame.transform.rotate(self._secondary_pygame_surface, self._angle)


        self._should_recompute_secondary_surface = False

    def is_clicked(self):
        return self._is_clicked

    def move(self, steps):
        self.x += steps

    def turn(self, degrees=10):
        self.angle += degrees

    @property 
    def transparency(self):
        return self._transparency

    @transparency.setter
    def transparency(self, alpha):
        if not isinstance(alpha, float) and not isinstance(alpha, int):
            raise Oops(f"""Looks like you're trying to set {self._image}'s transparency to '{alpha}', which isn't a number.
Try looking in your code for where you're setting transparency for {self._image} and change it a number.
""")
        if alpha > 100 or alpha < 0:
            _warnings.warn(f"""The transparency setting for {self} is being set to {alpha} and it should be between 0 and 100.
You might want to look in your code where you're setting transparency and make sure it's between 0 and 100.  """, Hmm)


        self._transparency = _clamp(alpha, 0, 100)
        self._should_recompute_secondary_surface = True

    @property 
    def image(self):
        return self._image

    @image.setter
    def image(self, image_filename):
        self._image = image_filename
        self._should_recompute_primary_surface = True

    @property 
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, _angle):
        self._angle = _angle
        self._should_recompute_secondary_surface = True

    @property 
    def size(self):
        return self._size

    @size.setter
    def size(self, percent):
        self._size = percent
        self._should_recompute_secondary_surface = True

    def hide(self):
        self._is_hidden = True

    def show(self):
        self._is_hidden = False

    def is_hidden(self):
        return self._is_hidden

    def is_shown(self):
        return not self._is_hidden

    def point_towards(self, x, y=None):
        try:
            x, y = x.x, x.y
        except AttributeError:
            pass
        self.angle = _math.degrees(_math.atan2(y-self.y, x-self.x))


    def go_to(self, x=None, y=None):
        """
        Example:

            # text will follow around the mouse
            text = play.new_text('yay')

            @play.repeat_forever
            async def do():
                text.go_to(play.mouse)
        """
        assert(not x is None)

        try:
            # users can call e.g. sprite.go_to(play.mouse), so x will be an object with x and y
            self.x = x.x
            self.y = x.y
        except AttributeError:
            self.x = x
            self.y = y 

    def distance_to(self, x=None, y=None):
        assert(not x is None)

        try:
            # x can either by a number or a sprite. If it's a sprite:
            x = x.x
            y = x.y
        except AttributeError:
            pass

        dx = self.x - x
        dy = self.y - y

        return _math.sqrt(dx**2 + dy**2)



    @property 
    def width(self):
        return self._secondary_pygame_surface.get_width()

    @property 
    def height(self):
        return self._secondary_pygame_surface.get_height()

    @property 
    def right(self):
        return self.x + self.width/2
    @right.setter
    def right(self, x):
        self.x = x - self.width/2

    @property 
    def left(self):
        return self.x - self.width/2
    @left.setter
    def left(self, x):
        self.x = x + self.width/2

    @property 
    def top(self):
        return self.y + self.height/2
    @top.setter
    def top(self, y):
        self.y = y - self.height/2

    @property 
    def bottom(self):
        return self.y - self.height/2
    @bottom.setter
    def bottom(self, y):
        self.y = y + self.height/2

    def _pygame_x(self):
        return self.x + (screen.width/2.) - (self._secondary_pygame_surface.get_width()/2.)

    def _pygame_y(self):
        return (screen.height/2.) - self.y - (self._secondary_pygame_surface.get_height()/2.)

    # @decorator
    def when_clicked(self, callback, call_with_sprite=False):
        async_callback = _make_async(callback)
        async def wrapper():
            wrapper.is_running = True
            if call_with_sprite:
                await async_callback(self)
            else:
                await async_callback()
            wrapper.is_running = False
        wrapper.is_running = False
        self._when_clicked_callbacks.append(wrapper)
        return wrapper

    def _common_properties(self):
        # used with inheritance to clone
        return {'x': self.x, 'y': self.y, 'size': self.size, 'transparency': self.transparency, 'angle': self.angle}

    def clone(self):
        return self.__class__(image=self.image, **self._common_properties())



def new_box(color='black', x=0, y=0, width=100, height=200, border_color='light blue', border_width=0, angle=0, transparency=100, size=100):
    return box(color=color, x=x, y=y, width=width, height=height, border_color=border_color, border_width=border_width, angle=angle, transparency=transparency, size=size)

class box(sprite):
    def __init__(self, color='black', x=0, y=0, width=100, height=200, border_color='light blue', border_width=0, transparency=100, size=100, angle=0):
        self.x = x
        self.y = y
        self._width = width
        self._height = height
        self._color = color
        self._border_color = border_color
        self._border_width = border_width

        self._transparency = transparency
        self._size = size
        self._angle = angle
        self._is_hidden = False

        self._when_clicked_callbacks = []

        self._compute_primary_surface()

        all_sprites.append(self)

    def _compute_primary_surface(self):
        self._primary_pygame_surface = pygame.Surface((self._width, self._height), pygame.SRCALPHA)


        if self._border_width and self._border_color:
            # draw border rectangle
            self._primary_pygame_surface.fill(_color_name_to_rgb(self._border_color))
            # draw fill rectangle over border rectangle at the proper position
            pygame.draw.rect(self._primary_pygame_surface, _color_name_to_rgb(self._color), (self._border_width,self._border_width,self._width-2*self._border_width,self._height-2*self.border_width))

        else:
            self._primary_pygame_surface.fill(_color_name_to_rgb(self._color))

        self._should_recompute_primary_surface = False
        self._compute_secondary_surface(force=True)


    ##### width #####
    @property 
    def width(self):
        return self._width

    @width.setter
    def width(self, _width):
        self._width = _width
        self._should_recompute_primary_surface = True


    ##### height #####
    @property 
    def height(self):
        return self._height

    @height.setter
    def height(self, _height):
        self._height = _height
        self._should_recompute_primary_surface = True


    ##### color #####
    @property 
    def color(self):
        return self._color

    @color.setter
    def color(self, _color):
        self._color = _color
        self._should_recompute_primary_surface = True

    ##### border_color #####
    @property 
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, _border_color):
        self._border_color = _border_color
        self._should_recompute_primary_surface = True

    ##### border_width #####
    @property 
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, _border_width):
        self._border_width = _border_width
        self._should_recompute_primary_surface = True

    def clone(self):
        return self.__class__(color=self.color, width=self.width, height=self.height, border_color=self.border_color, border_width=self.border_width, **self._common_properties())

def new_circle(color='black', x=0, y=0, radius=100, border_color='light blue', border_width=0, transparency=100, size=100, angle=0):
    return circle(color=color, x=x, y=y, radius=radius, border_color=border_color, border_width=border_width,
        transparency=transparency, size=size, angle=angle)



class circle(sprite):
    def __init__(self, color='black', x=0, y=0, radius=100, border_color='light blue', border_width=0, transparency=100, size=100, angle=0):
        self.x = x
        self.y = y
        self._color = color
        self._radius = radius
        self._border_color = border_color
        self._border_width = border_width

        self._transparency = transparency
        self._size = size
        self._angle = angle
        self._is_hidden = False

        self._when_clicked_callbacks = []

        self._compute_primary_surface()

        all_sprites.append(self)

    def clone(self):
        return self.__class__(color=self.color, radius=self.radius, border_color=self.border_color, border_width=self.border_width, **self._common_properties())

    def _compute_primary_surface(self):
        total_diameter = (self._radius + self._border_width) * 2
        self._primary_pygame_surface = pygame.Surface((total_diameter, total_diameter), pygame.SRCALPHA)


        center = self._radius + self._border_width

        if self._border_width and self._border_color:
            # draw border circle
            pygame.draw.circle(self._primary_pygame_surface, _color_name_to_rgb(self._border_color), (center, center), self._radius)
            # draw fill circle over border circle
            pygame.draw.circle(self._primary_pygame_surface, _color_name_to_rgb(self._color), (center, center), self._radius-self._border_width)

        else:
            pygame.draw.circle(self._primary_pygame_surface, _color_name_to_rgb(self._color), (center, center), self._radius)

        self._should_recompute_primary_surface = False
        self._compute_secondary_surface(force=True)

    ##### color #####
    @property 
    def color(self):
        return self._color

    @color.setter
    def color(self, _color):
        self._color = _color
        self._should_recompute_primary_surface = True

    ##### radius #####
    @property 
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, _radius):
        self._radius = _radius
        self._should_recompute_primary_surface = True

    ##### border_color #####
    @property 
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, _border_color):
        self._border_color = _border_color
        self._should_recompute_primary_surface = True

    ##### border_width #####
    @property 
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, _border_width):
        self._border_width = _border_width
        self._should_recompute_primary_surface = True


def new_text(words='hi :)', x=0, y=0, font=None, font_size=50, color='black', angle=0, transparency=100, size=100):
    return text(words=words, x=x, y=y, font=font, font_size=font_size, color=color, angle=angle, transparency=transparency, size=size)

class text(sprite):
    def __init__(self, words='hi :)', x=0, y=0, font=None, font_size=50, color='black', angle=0, transparency=100, size=100):
        self._words = words
        self.x = x
        self.y = y
        self._font = font
        self._font_size = font_size
        self._color = color
        self._size = size
        self._angle = angle
        self.transparency = transparency

        self._is_clicked = False
        self._is_hidden = False

        self._compute_primary_surface()

        self._when_clicked_callbacks = []

        all_sprites.append(self)

    def clone(self):
        return self.__class__(words=self.words, font=self.font, font_size=self.font_size, color=self.color, **self._common_properties())

    def _compute_primary_surface(self):
        try:
            self._pygame_font = pygame.font.Font(self._font, self._font_size)
        except:
            _warnings.warn(f"""We couldn't find the font file '{self._font}'. We'll use the default font instead for now.
To fix this, either set the font to None, or make sure you have a font file (usually called something like Arial.ttf) in your project folder.\n""", Hmm)
            self._pygame_font = pygame.font.Font(None, self._font_size)

        self._primary_pygame_surface = self._pygame_font.render(self._words, True, _color_name_to_rgb(self._color))
        self._should_recompute_primary_surface = False

        self._compute_secondary_surface(force=True)

    @property
    def words(self):
        return self._words

    @words.setter
    def words(self, string):
        self._words = str(string)
        self._should_recompute_primary_surface = True

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, font_name):
        self._font = str(font_name)
        self._should_recompute_primary_surface = True

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, size):
        self._font_size = size
        self._should_recompute_primary_surface = True

    @property 
    def color(self):
        return self._color

    @color.setter
    def color(self, color_):
        self._color = color_
        self._should_recompute_primary_surface = True




# @decorator
def when_sprite_clicked(*sprites):
    def wrapper(func):
        for sprite in sprites:
            sprite.when_clicked(func, call_with_sprite=True)
        return func
    return wrapper

pygame.key.set_repeat(200, 16)
_pressed_keys = {}
_keypress_callbacks = []
_keyrelease_callbacks = []

# @decorator
def when_any_key_pressed(func):
    if not callable(func):
        raise Oops("""@play.when_any_key_pressed doesn't use a list of keys. Try just this instead:

@play.when_any_key_pressed
async def do(key):
    print("This key was pressed!", key)
""")
    async_callback = _make_async(func)
    async def wrapper(*args, **kwargs):
        wrapper.is_running = True
        await async_callback(*args, **kwargs)
        wrapper.is_running = False
    wrapper.keys = None
    wrapper.is_running = False
    _keypress_callbacks.append(wrapper)
    return wrapper

# @decorator
def when_key_pressed(*keys):
    def decorator(func):
        async_callback = _make_async(func)
        async def wrapper(*args, **kwargs):
            wrapper.is_running = True
            await async_callback(*args, **kwargs)
            wrapper.is_running = False
        wrapper.keys = keys
        wrapper.is_running = False
        _keypress_callbacks.append(wrapper)
        return wrapper
    return decorator

# @decorator
def when_any_key_released(func):
    if not callable(func):
        raise Oops("""@play.when_any_key_released doesn't use a list of keys. Try just this instead:

@play.when_any_key_released
async def do(key):
    print("This key was released!", key)
""")
    async_callback = _make_async(func)
    async def wrapper(*args, **kwargs):
        wrapper.is_running = True
        await async_callback(*args, **kwargs)
        wrapper.is_running = False
    wrapper.keys = None
    wrapper.is_running = False
    _keyrelease_callbacks.append(wrapper)
    return wrapper

# @decorator
def when_key_released(*keys):
    def decorator(func):
        async_callback = _make_async(func)
        async def wrapper(*args, **kwargs):
            wrapper.is_running = True
            await async_callback(*args, **kwargs)
            wrapper.is_running = False
        wrapper.keys = keys
        wrapper.is_running = False
        _keyrelease_callbacks.append(wrapper)
        return wrapper
    return decorator

def key_is_pressed(*keys):
    """
    Returns True if any of the given keys are pressed.

    Example:

        @play.repeat_forever
        async def do():
            if play.key_is_pressed('up', 'w'):
                print('up or w pressed')
    """
    # Called this function key_is_pressed instead of is_key_pressed so it will
    # sound more english-like with if-statements:
    #
    #   if play.key_is_pressed('w', 'up'): ...

    for key in keys:
        if key in _pressed_keys.values():
            return True
    return False

_loop = _asyncio.get_event_loop()
_loop.set_debug(False)

_keys_pressed_this_frame = []
_keys_released_this_frame = []
_keys_to_skip = [pygame.K_MODE]
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION])
_clock = pygame.time.Clock()
def _game_loop():
    _keys_pressed_this_frame.clear() # do this instead of `_keys_pressed_this_frame = []` to save a tiny bit of memory
    _keys_released_this_frame.clear()
    click_happened_this_frame = False
    click_release_happened_this_frame = False

    _clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q and (pygame.key.get_mods() & pygame.KMOD_META or pygame.key.get_mods() & pygame.KMOD_CTRL)):
            # quitting by clicking window's close button or pressing ctrl+q / command+q
            _loop.stop()
            return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_happened_this_frame = True
            mouse._is_clicked = True
        if event.type == pygame.MOUSEBUTTONUP:
            click_release_happened_this_frame = True
            mouse._is_clicked = False
        if event.type == pygame.MOUSEMOTION:
            mouse.x, mouse.y = (event.pos[0] - screen.width/2.), (screen.height/2. - event.pos[1])
        if event.type == pygame.KEYDOWN:
            if not (event.key in _keys_to_skip):
                name = _pygame_key_to_name(event)
                _pressed_keys[event.key] = name
                _keys_pressed_this_frame.append(name)
        if event.type == pygame.KEYUP:
            if not (event.key in _keys_to_skip):
                _keys_released_this_frame.append(_pressed_keys[event.key])
                del _pressed_keys[event.key]



    ############################################################
    # @when_any_key_pressed and @when_key_pressed callbacks
    ############################################################
    for key in _keys_pressed_this_frame:
        for callback in _keypress_callbacks:
            if not callback.is_running and (callback.keys is None or key in callback.keys):
                _loop.create_task(callback(key))

    ############################################################
    # @when_any_key_released and @when_key_released callbacks
    ############################################################
    for key in _keys_released_this_frame:
        for callback in _keyrelease_callbacks:
            if not callback.is_running and (callback.keys is None or key in callback.keys):
                _loop.create_task(callback(key))


    ####################################
    # @mouse.when_clicked callbacks
    ####################################
    if click_happened_this_frame and mouse._when_clicked_callbacks:
        for callback in mouse._when_clicked_callbacks:
            if not callback.is_running:
                _loop.create_task(callback())

    ####################################
    # @mouse.when_click_released callbacks
    ####################################
    if click_release_happened_this_frame and mouse._when_click_released_callbacks:
        for callback in mouse._when_click_released_callbacks:
            if not callback.is_running:
                _loop.create_task(callback())


    #############################
    # @repeat_forever callbacks
    #############################
    for callback in _repeat_forever_callbacks:
        if not callback.is_running:
            _loop.create_task(callback())

    # 1.  get pygame events
    #       - set mouse position, clicked, keys pressed, keys released
    # 2.  run when_program_starts callbacks
    # 3.  run physics simulation
    # 4.  compute new pygame_surfaces (scale, rotate)
    # 5.  run repeat_forever callbacks
    # 6.  run mouse/click callbacks (make sure more than one isn't running at a time)
    # 7.  run keyboard callbacks (make sure more than one isn't running at a time)
    # 8.  run when_touched callbacks
    # 9.  render background
    # 10. render sprites (with correct z-order)
    # 11. call event loop again



    _pygame_display.fill(_color_name_to_rgb(background_color))

    # BACKGROUND COLOR
    # note: cannot use screen.fill((1, 1, 1)) because pygame's screen
    #       does not support fill() on OpenGL surfaces
    # gl.glClearColor(_background_color[0], _background_color[1], _background_color[2], 1)
    # gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    for sprite in all_sprites:

        sprite._is_clicked = False

        if sprite.is_hidden():
            continue


        #################################
        # @sprite.when_clicked events
        #################################
        if mouse.is_clicked():
            # get_rect().collidepoint() is local coordinates, e.g. 100x100 image, so have to translate
            if sprite._secondary_pygame_surface.get_rect().collidepoint((mouse.x+screen.width/2.)-sprite._pygame_x(), (screen.height/2.-mouse.y)-sprite._pygame_y()):
                sprite._is_clicked = True

                # only run sprite clicks on the frame the mouse was clicked
                if click_happened_this_frame:
                    for callback in sprite._when_clicked_callbacks:
                        if not callback.is_running:
                            _loop.create_task(callback())


        # do sprite image transforms (re-rendering images/fonts, scaling, rotating, etc)

        # we put it in the event loop instead of just recomputing immediately because if we do it
        # synchronously then the data and rendered image may get out of sync
        if sprite._should_recompute_primary_surface:
            # recomputing primary surface also recomputes secondary surface
            _loop.call_soon(sprite._compute_primary_surface)
        elif sprite._should_recompute_secondary_surface:
            _loop.call_soon(sprite._compute_secondary_surface)

        _pygame_display.blit(sprite._secondary_pygame_surface, (sprite._pygame_x(), sprite._pygame_y()) )

    pygame.display.flip()
    _loop.call_soon(_game_loop)
    return True


async def timer(seconds=1.0):
    await _asyncio.sleep(seconds)
    return True

async def animate():
    await _asyncio.sleep(0)

_repeat_forever_callbacks = []
# @decorator
def repeat_forever(func):
    """
    Calls the given function repeatedly.

    Example:

        text = play.new_text(words='hi there!', x=0, y=0, font='Arial.ttf', font_size=20, color='black')

        @play.repeat_forever
        async def do():
            text.turn(degrees=15)

    """
    async_callback = _make_async(func)
    async def repeat_wrapper():
        repeat_wrapper.is_running = True
        await async_callback()
        repeat_wrapper.is_running = False

    repeat_wrapper.is_running = False
    _repeat_forever_callbacks.append(repeat_wrapper)
    return func


_when_program_starts_callbacks = []
# @decorator
def when_program_starts(func):
    async_callback = _make_async(func)
    async def wrapper(*args, **kwargs):
        return await async_callback(*args, **kwargs)
    _when_program_starts_callbacks.append(wrapper)
    return func

def repeat(number_of_times):
    return range(1, number_of_times+1)

def start_program():
    for func in _when_program_starts_callbacks:
        _loop.create_task(func())

    _loop.call_soon(_game_loop)
    try:
        _loop.run_forever()
    finally:
        _logging.getLogger("asyncio").setLevel(_logging.CRITICAL)
        pygame.quit()



"""
cool stuff to add:
    scene class, hide and show scenes in one go (collection of sprites)
    ellipse
    collision system (bouncing balls, platformer)
    play.mouse.is_touching()
    @sprite.when_touched

    sprite.glide_to(other_sprite, seconds=1)
    sprite.remove()
    dog.go_to(cat.bottom) # dog.go_to(cat.bottom+5)
    play sound / music
    play.music('jam.mp3', loop=False)
    play.stop_music('jam.mp3')
    play.sound('jam.mp3')
    play.volume = 2
    sprite.is_touching(cat)
    play.gravity(vertical=1.0, horizontal=0)
    sprite.physics( x_velocity, y_velocity, obeys_gravity=True, bounces_off_walls=True, heaviness=1, bounciness=1.0)
        sprite.physics_off()
        sprite.is_physics_on()
        box2d is_fixed_rotation good for platformers
    play.background_image('backgrounds/waterfall.png', fit_to_screen=False, x=0,y=0)
    sprite.flip(direction='left-right') sprite.flip(direction='up-down')
    sprite.flip(left_right=True, up_down=False)

    maybe use pygame.text at some point: https://github.com/cosmologicon/pygame-text - make play.new_text_extra()
    text.wrapping = True

    add pygame images to cache for fast new sprite creation (reuse image.png, font)




[ ] how to make a text input box simply?
[ ] how to make paint app?
[ ] how to make midi keyboard app?
[ ] how to make simple jumping box character with gravity?
[ ] how to make more advanced platformer?
[ ] how to make shooter? http://osmstudios.com/tutorials/your-first-love2d-game-in-200-lines-part-1-of-3
[ ] how to make point and click tic-tac-toe?

funny game idea: pong game where paddle shrinks unless you get powerups that spawn randomly in your zone


IDE ideas:
    - add helpful comment about any code appearing below play.start_program() not running. I made this mistake and it was confusing
    - if pasting in event code (e.g. @play.when_key_pressed async def do(key)), make the indent level all the way to the left
    - if pasting in sprite code (e.g. hide()), find the last defined sprite before the cursor and call the method on that.
    - if command doesn't have visible effect (i.e. is_hidden()), print it or create a conditional (if sprite.is_hidden(): print("the sprite is hidden"))
    - if pasting in awaitable code (e.g. await play.timer(seconds=1.0)), somehow make sure it's in an async function
    - if possible, always paste full working example code that will do something visible
"""
