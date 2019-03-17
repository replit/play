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


## How to use Python Play

All Python Play programs start with `import play` and end with `play.start_program()`, like this:

```python
import play


play.start_program()
```

All other commands go between those two commands.

To try any of the following examples, go to **[repl.it and change the code](TODO)**

### Basic Commands

To get images or text on the screen, use `play.new_sprite()` and `play.new_text()`.

```python
character = play.new_sprite(image='character.png', x=0, y=0, size=100, transparency=100)
```


```python
speech = play.new_text(words='hey there', x=0, y=0, font='', font_size=50, color='black', transparency=100)
```



### Control

`@play.repeat_forever`

`@play.when_program_starts`

`await play.timer(seconds=1)`

`await play.animate()`

`play.start_program()`

### Keyboard 

`@play.when_any_key_pressed`

`@play.when_key_pressed()`

`play.key_is_pressed()`


### Mouse

`@play.when_mouse_clicked`

`@play.when_sprite_clicked()`

--
`play.mouse`

`@play.mouse.when_clicked`

`play.mouse.is_clicked()`

`play.mouse.x, play.mouse.y`

--

`@sprite.when_clicked`


### Sprites


image
x,y
size
angle
transparency
width
height

`sprite.move()`

`sprite.turn()`

`sprite.go_to()`

`sprite.point_towards()`

--

`sprite.hide()`

`sprite.show()`

--

`sprite.distance_to()`

--

`sprite.is_clicked()`

`sprite.is_hidden()`

`sprite.is_shown()`



### Other Commands

`play.random_number()`

`play.random_color()`

`play.set_background_color()`

`await play.animate()`