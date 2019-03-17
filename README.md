# Python Play (beta)
## The easiest way to start coding games and graphics projects in Python

Python Play is an open-source code library for the Python programming language that makes it as easy as possible to start making games. Here's the code to make a simple game using Play:

```python
import play

cat = play.new_text('=^.^=', font_size=70)

@play.repeat_forever
async def do():
    cat.x = play.random_number(-200, 200)
    cat.y = play.random_number(-200, 200)
    cat.color = play.random_color()
    
    cat.show()

    await play.timer(seconds=0.4)

    cat.hide()

    await play.timer(seconds=0.4)

@cat.when_clicked
async def do():
    cat.show()
    cat.words = 'You won!'

play.start_program()
```

The code above makes a game where you have to click the cat to win:

![Clicking a cat game](example.gif)

[You can try playing and changing this game on repl.it!](TODO)


# How to use Python Play

All Python Play programs start with `import play` and end with `play.start_program()`, like this:

```python
import play


play.start_program()
```

All other commands go between those two commands.

To try any of the following examples, go to **[repl.it and try pasting code in](TODO)**.

## Basic Commands

To get images or text on the screen, use `play.new_sprite()` and `play.new_text()`. (Copy and paste the code below to try it out.)

#### `play.new_sprite()`
```python
character = play.new_sprite(image='character.png', x=0, y=0, angle=0, size=100, transparency=100)
```

This will place an image in the middle of the screen. Make sure you have a file named `character.png` in your project files for the code above to work.

If you want to change where the image is on the screen, try changing `x=0` (horizontal position) and `y=0` (vertical position). Positive x is to the right and positive y is up.

#### `play.new_text()`
```python
greeting = play.new_text(words='hey there', x=50, y=0, angle=0, font=None, font_size=50, color='black', transparency=100)
```

This will put some text on the screen.

If you want to change the font, you'll need a font file (usually named something like `Arial.ttf`) in your project files. Then you can change `font=None` to `font='Arial.ttf'`.


#### `play.set_background_color()`
You can also change the background color with the `play.set_background_color()` command:

```python
play.set_background_color('light blue')
```

There are [lots of named colors to choose from](https://upload.wikimedia.org/wikipedia/commons/2/2b/SVG_Recognized_color_keyword_names.svg). Additionally, if you want to set colors by RGB (Red Green Blue) values, you can do that like this:

```python
# sets the background to white
play.set_background_color( (255, 255, 255) )
# each number can go from 0 to 255
```




## Animation Commands

#### `@play.repeat_forever`
To make things move around, you can start by using `@play.repeat_forever`, like this:

```python
cat = play.new_text('=^.^=')

@play.repeat_forever
async def do():

    cat.turn(10)  
```    

The above code will make the cat turn around forever. Sprites have other commands that you can see in the next section called Sprite Commands.

#### `@play.when_program_starts`

To make some code run just at the beginning of your project, use `@play.when_program_starts`, like this:

```python
cat = play.new_text('=^.^=')

@play.when_program_starts
async def do():

    cat.turn(180)  
```

This will make the cat turn upside down instantly when the program starts.


#### `await play.timer(seconds=1)`

To run code after a waiting period, you can use the `await play.timer()` command like this:

```python
cat = play.new_text('=^.^=')

@play.when_program_starts
async def do():

    cat.turn(180)  
    await play.timer(seconds=2)
    cat.turn(180)  
```

This will make the cat turn upside down instantly when the program starts, wait 2 seconds, then turn back up again.


#### `play.repeat()` and `await play.animate()`

To smoothly animate a character a certain number of times, you can use `play.repeat()` with `await play.animate()`, like this:


```python
cat = play.new_text('=^.^=')

@play.when_program_starts
async def do():
    for count in play.repeat(180):
        cat.turn(1)
        await play.animate()
```

This code will animate the cat turning upside down smoothly when the program starts.

To break down the code:
- `for count in play.repeat(180):` runs the code 180 times.
- `cat.turn(1)` turns that cat 1 degree each time.
- `await play.animate()` makes the cat animate smoothly. Without this command, the cat would just turn upside down instantly.






## Sprite Commands


#### Simple commands

Sprites (images and text) have a few simple commands:

- **`sprite.move(10)`** — moves the sprite 10 pixels in the direction it's facing (starts facing right). Use negative numbers (-10) to go backward.
- **`sprite.turn(20)`** — Turns the sprite 20 degrees clockwise. Use negative numbers (-20) to turn the other way.
- **`sprite.go_to(other_sprite)`** — Makes `sprite` go to another sprite named `other_sprite`'s position on the screen.
- **`sprite.go_to(x=100, y=50)`** — Makes `sprite` go to x=100, y=50 (right and up a little).
- **`sprite.point_towards(other_sprite)`** — Turns `sprite` so it points at another sprite called `other_sprite`.
- **`sprite.hide()`** — Hides `sprite`. It can't be clicked when it's hidden.
- **`sprite.show()`** — Shows `sprite` if it's hidden.

#### Properties

Sprites also have properties that can be changed to change how the sprite looks. Here they are:

- **`sprite.x`** — The sprite's horizontal position on the screen. Positive numbers are right, negative numbers are left. The default is 0.
- **`sprite.y`** — The sprite's vertical position on the screen. Positive numbers are up, negative numbers are down. The default is 0.
- **`sprite.size`** — How big the sprite is from 0 to 100. The default is 100.
- **`sprite.angle`** — How turned the sprite is. Positive numbers are clockwise. The default is 0 degrees (pointed to the right).
- **`sprite.transparency`** — How see-through the sprite is from 0 to 100. 0 is completely see-through, 100 is not see-through at all. The default is 100.

These properties can changed to do the same things as the commands above. For example,

```python
sprite.go_to(other_sprite)

# the line above is the same as the two lines below

sprite.x = other_sprite.x
sprite.y = other_sprite.y
```

You can change the properties to animate the sprites:

```python
cat = play.new_text('=^.^=')

@play.repeat_forever
async def do():
    cat.angle += 1
    # the line above is the same as cat.turn(1)
```

The code above makes the cat turn around.


#### Other info

Sprites also have some other useful info:

- **`sprite.width`** — Gets how wide the sprite is in pixels.
- **`sprite.height`** — Gets how tall the sprite is in pixels.
- **`sprite.left`** — Gets the x position of the left-most part of the sprite.
- **`sprite.right`** — Gets the x position of the right-most part of the sprite.
- **`sprite.top`** — Gets the y position of the top-most part of the sprite.
- **`sprite.bottom`** — Gets the y position of the bottom-most part of the sprite.
- **`sprite.distance_to(other_sprite)`** — Gets the distance in pixels to `other_sprite`.
- **`sprite.distance_to(x=100, y=100)`** — Gets the distance to the point x=100, y=100.
- **`sprite.is_clicked()`** — Returns True if the sprite has been clicked this frame. Otherwise returns False.
- **`sprite.is_hidden()`** — Returns True if the sprite has been hidden with the `sprite.hide()` commands. Otherwise returns False.
- **`sprite.is_shown()`** — Returns True if the sprite has not been hidden with the `sprite.hide()` command. Otherwise returns False.





## Mouse Commands

`@sprite.when_clicked`

`@play.when_mouse_clicked`

`@play.when_sprite_clicked()`

--
`play.mouse`

`@play.mouse.when_clicked`

`play.mouse.is_clicked()`

`play.mouse.x, play.mouse.y`





## Keyboard Commands

`@play.when_any_key_pressed`

`@play.when_key_pressed()`

`play.key_is_pressed()`



--






## Other Useful Commands

#### `play.random_number()`

A function that makes random numbers.

If two whole numbers are given, `play.random_number()` will give a whole number back:

```python
play.random_number(lowest=0, highest=100)
# the same as play.random_number(0, 100)

# example return value: 42
```

If non-whole numbers are given, non-whole numbers are given back:

```python
play.random_number(0, 1.0)
# example return value: 0.84
```

`play.random_number() is also inclusive, which means `play.random_number(0,1)` will return `0` and `1`.


#### `play.random_color()`

Returns a random RGB color, including white and black.

```python
play.random_color()
# example return value: (201, 17, 142)
```

#### `play.repeat()`

The same as Python's built-in `range` function, except it starts at 1. 'Repeat' is just a friendlier and more descriptive name than 'range'.

```python
list(play.repeat(10))
# return value: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

#### `await play.animate()`

When used in a loop, this command will animate any sprite changes that happen.

```python
cat = play.new_text('=^.^=')

@play.when_program_starts
async def do():
    for count in play.repeat(360):
        cat.turn(1)
        await play.animate()
```

`await play.animate()` is the same as `await asyncio.sleep(0)`.


## What's with all this `async`/`await` stuff? Is this Python?

Yes, this is Python! Python added `async` and `await` as special keywords in Python 3.7. It's part of the [asyncio module](https://docs.python.org/3/library/asyncio.html).

What that means for this library is that we can use async functions to help us run animations. For example,

```python
import play

cat = play.new_text('=^.^=')

@play.repeat_forever
async def do():
    play.set_background_color('pink')
    await play.timer(seconds=1)

    play.set_background_color('purple')
    await play.timer(seconds=1)

    play.set_background_color('light blue')
    await play.timer(seconds=1)

@play.repeat_forever
async def do():
    cat.turn(1)

play.start_program()
```

Both of the `@play.repeat_forever` blocks will run seemingly at the same time, which makes the code look a lot simpler for new programmers.

Although it's annoying to have to type `async` before procedure definitions, we think the trade-off is worth it. Plus, we'd hope your IDE would be good enough so that brand new programmers don't have to type this stuff.