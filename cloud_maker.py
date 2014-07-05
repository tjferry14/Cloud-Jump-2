import Image, ImageDraw, random, scene

def generate_shapes(num_circles):
    shapes = []
    for i in xrange(num_circles):
        x = (i * 20 - ((num_circles/2)*30))+90
        y = ((random.random()-0.5) * 30)+15
        rad = random.randint(50, 100)
        shapes.append([x, y, rad])
    return shapes

def cloud_maker():
    num_circles = random.randint(5, 6)
    image_size = (220, 140)
    theImage = Image.new('RGBA', image_size)
    draw = ImageDraw.Draw(theImage)

    circles = generate_shapes(num_circles)
    for i in circles:
        r = i[2]
        bbox = (i[0], 40-i[1], i[0]+r, 40-i[1]+r)
        draw.ellipse(bbox, fill='rgb(90%,90%,90%)')
    for i in circles:
        r = i[2]
        bbox = (i[0], 40-i[1]-10, i[0]+r, 40-i[1]+r-10)
        draw.ellipse(bbox, fill='white')

    del draw
    return theImage

class Cloud(scene.Layer):
    def __init__(self, parent = None):
        cloud_image = cloud_maker()
        super(self.__class__, self).__init__(scene.Rect(*cloud_image.getbbox()))
        if parent:
            parent.add_layer(self)
        self.image = scene.load_pil_image(cloud_image)

class MyScene(scene.Scene):
    def __init__(self):
        scene.run(self)

    def setup(self):
        self.cloud = Cloud(self)
        self.cloud.frame.center(self.bounds.center())

    def draw(self):
        scene.background(0.40, 0.80, 1.00)
        self.root_layer.update(self.dt)
        self.root_layer.draw()
        #scene.rect(*self.cloud.frame)

    def touch_began(self, touch):
        self.root_layer.remove_layer(self.cloud)
        self.setup()

MyScene()
