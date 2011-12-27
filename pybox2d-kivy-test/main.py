from Box2D import *

from random import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from kivy.lang import Builder
from kivy.clock import Clock

Builder.load_string('''
<Circle>:
    canvas:
        Color:
            hsv: self.hue, 1, 1
        Ellipse:
            pos: self.x - self.radius, self.y - self.radius
            size: self.radius * 2, self.radius * 2
''')

class Circle(Widget):
    radius = NumericProperty(20)
    hue = NumericProperty(0)

    # for physics
    world = ObjectProperty(None)
    _body = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(Circle, self).__init__(**kwargs)
        self.hue = random()

        bodyDef = b2BodyDef()
        bodyDef.position = self.pos
        self._body = body = self.world.CreateBody(bodyDef)
        # Define another box shape for our dynamic body.
        shapeDef = b2CircleDef()
        shapeDef.radius = self.radius
        # Set the box density to be non-zero, so it will be dynamic.
        shapeDef.density = 1
        # Override the default friction.
        shapeDef.friction = 0.3
        # Add the shape to the body.
        shape = body.CreateShape(shapeDef)
        # Now tell the dynamic body to compute it's mass properties base on its shape.
        body.SetMassFromShapes()

    def update_from_body(self):
        self.pos = self._body.position.x, self._body.position.y

class PhysicsApp(App):
    def generate_one(self, instance, touch):
        c = Circle(pos=touch.pos, world=self.world)
        self.circles.append(c)
        self.root.add_widget(c)

    def build(self):
        root = Widget()
        root.bind(on_touch_move=self.generate_one)
        aabb = b2AABB()
        aabb.lowerBound = b2Vec2(0, 0)
        aabb.upperBound = b2Vec2(10000, 10000)
        self.world = world = b2World(
                aabb, b2Vec2(0, -100), True)

        # plane for the ground, all other the window.
        # Define the ground body.
        groundBodyDef = b2BodyDef()
        groundBodyDef.position = [0, 0]
        # Call the body factory which allocates memory for the ground body
        # from a pool and creates the ground box shape (also from a pool).
        # The body is also added to the world.
        groundBody = world.CreateBody(groundBodyDef)
        # Define the ground box shape.
        groundShapeDef = b2PolygonDef()
        # The extents are the half-widths of the box.
        groundShapeDef.SetAsBox(10000, 1)
        # Add the ground shape to the ground body.
        groundBody.CreateShape(groundShapeDef)

        # generate circles
        self.circles = []
        for x in xrange(5):
            c = Circle(y=500 + x * 5, x=500+x, world=world)
            self.circles.append(c)
            root.add_widget(c)
        Clock.schedule_interval(self._update_world, 1 / 60.)

        return root

    def _update_world(self, dt):
        self.world.Step(dt, 10, 8)
        for child in self.circles:
            child.update_from_body()

if __name__ == '__main__':
    PhysicsApp().run()
