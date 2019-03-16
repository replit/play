# Python Play (beta)
## A simple way to start making games and media in Python

Play is a code library for the Python programming language that makes it as easy as possible to start making games. Here's the code to make a simple game using Play:

```python
import play



play.start_program()
```

This code produces a game that looks like this:

    gif

[You can try running and changing this code on repl.it!](todo)


## Commands

`play.new_sprite()`

`play.new_text()`

`play.set_background_color()`

## Control

`@play.repeat_forever`

`@play.when_program_starts`

`await play.timer(seconds=1)`

`await play.animate()`

`play.start_program()`

## Keyboard 

`@play.when_any_key_pressed`

`@play.when_key_pressed()`

`play.key_is_pressed()`


## Mouse

`@play.when_mouse_clicked`

`@play.when_sprite_clicked()`

--
`play.mouse`

`@play.mouse.when_clicked`

`play.mouse.is_clicked()`

`play.mouse.x, play.mouse.y`

--

`@sprite.when_clicked`


## Sprites


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

