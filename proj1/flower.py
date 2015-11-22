import turtle

def petal(t, r, angle):
    """Use the Turtle (t) to draw a petal using two arcs
    with the radius (r) and angle.
    """
    for i in range(2):
        t.circle(r,angle)
        t.left(180-angle)

def flower(t, n, r, angle):
    """Use the Turtle (t) to draw a flower with (n) petals,
    each with the radius (r) and angle.
    """
    for i in range(n):
        petal(t, r, angle)
        t.left(360.0/n)
        #t.left(180.0/n)

def move(t, length):
    """Move Turtle (t) forward (length) units without leaving a trail.
    Leaves the pen down.
    """
    t.pu()
    t.fd(length)
    t.pd()


painter = turtle.Pen()

painter.speed(0)

painter.shape("turtle")
painter.color("blue")
move(painter, 100)
flower(painter, 40, 40.0, 80.0)
painter.right(90)
painter.forward(150)

turtle.exitonclick()
