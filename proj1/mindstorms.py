import turtle
import time

painter = turtle.Turtle()
def draw_square():
    window = turtle.Screen()
    window.bgcolor("red")

    painter.shape("turtle")
    painter.color("yellow")
    painter.speed(2)

    for i in range(0, 4) :
        painter.forward(100)
        painter.right(90)

def draw_circle():
    angie = turtle.Turtle()
    angie.shape("arrow")
    angie.color("blue")
    angie.circle(100)

def draw_triangle():
    sam = turtle.Turtle()
    sam.shape("arrow")
    sam.color("white")
    sam.left(180)
    sam.forward(100)
    sam.left(90)
    sam.forward(100)
    sam.left(135)
    sam.forward(141.42)
    time.sleep(3)

for i in range(0, 36) :
   draw_square()
   painter.right(10)

#draw_circle()
#draw_triangle()
