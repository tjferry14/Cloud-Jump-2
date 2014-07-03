import Image, ImageDraw, random, scene

def generate_shapes(num_circles = random.randint(4, 5)):
    shapes = []
    for i in xrange(num_circles):
        x = i * 20 - ((num_circles/2)*30)
        y = (random.random()-0.5) * 30
        x += 60  # this is a hack!
        y += 16  # this is a hack!
        rad = random.randint(50, 100)
        shapes.append([x, y, rad])
    return shapes

def cloud_maker():
    num_circles = random.randint(4, 5)
    #image_size = ((num_circles + 1) * 30, 60)
    image_size = (180, 128)
    theImage = Image.new('RGBA', image_size) #, 'pink')
    draw = ImageDraw.Draw(theImage)
    
    circles = generate_shapes(num_circles)
    for i in circles:
        bbox = (i[0], i[1] - 5, i[2], i[2])
        draw.ellipse(bbox, fill='rgb(90%,90%,90%)')
    for i in circles:
        bbox = (i[0], i[1] + 5, i[2], i[2])
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
        self.cloud.frame.x = 0
        self.cloud.frame.y = self.bounds.h * 0.8

    def draw(self):
        scene.background(0.40, 0.80, 1.00)
        self.root_layer.update(self.dt)
        self.root_layer.draw()
        self.cloud.frame.x += 1
        if not self.bounds.intersects(self.cloud.frame):
            del self.cloud  # whack the old cloud
            self.setup()    # and create a new one

MyScene()
