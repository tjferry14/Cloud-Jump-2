import Image, ImageDraw, random, scene
import numpy as np

class Cloud(scene.Layer):
    def __init__(self, parent = None):
        cloud_image = self.cloud_maker()
        super(self.__class__, self).__init__(scene.Rect(*cloud_image.getbbox()))
        if parent:
            parent.add_layer(self)
        self.image = scene.load_pil_image(cloud_image)
        self.background = scene.Color(1, 0, 1)  # comment out to hide the frame

    @classmethod
    def generate_shapes(cls, num_circles):
        shapes = []
        for i in xrange(num_circles):
            x = (i * 20 - ((num_circles/2)*30))+90
            y = ((random.random()-0.5) * 30)+15
            rad = random.randint(50, 100)
            shapes.append([x, y, rad])
        return shapes

    @classmethod
    def draw_cloud(cls, draw):
        num_circles = random.randint(5, 6)
        circles = cls.generate_shapes(num_circles)
        for i in circles:
            r = i[2]
            bbox = (i[0], 40-i[1], i[0]+r, 40-i[1]+r)
            draw.ellipse(bbox, fill='rgb(90%,90%,90%)')
        for i in circles:
            r = i[2]
            bbox = (i[0], 40-i[1]-10, i[0]+r, 40-i[1]+r-10)
            draw.ellipse(bbox, fill='white')

    # found on 'http://stackoverflow.com/questions/14211340/automatically-cropping-an-image-with-python-pil'
    @classmethod
    def crop_image(cls, img):
        image_data = np.asarray(img)
        image_data_bw = image_data.max(axis=2)
        non_empty_columns = np.where(image_data_bw.max(axis=0)>0)[0]
        non_empty_rows    = np.where(image_data_bw.max(axis=1)>0)[0]
        crop_box = (min(non_empty_rows),    max(non_empty_rows),
                    min(non_empty_columns), max(non_empty_columns))
        image_data_new = image_data[crop_box[0]:crop_box[1]+1,
                                    crop_box[2]:crop_box[3]+1, :]
        img = Image.fromarray(image_data_new)
        return img

    @classmethod
    def cloud_maker(cls):
        image_size = (220, 140)
        img = Image.new('RGBA', image_size)
        draw = ImageDraw.Draw(img)
        cls.draw_cloud(draw)
        del draw
        return cls.crop_image(img)

class MyScene(scene.Scene):
    def __init__(self):
        scene.run(self)
        self.cloud = None

    def setup(self):
        if self.cloud:
            self.root_layer.remove_layer(self.cloud)
        self.cloud = Cloud(self)
        self.cloud.frame.center(self.bounds.center())

    def draw(self):
        scene.background(0.40, 0.80, 1.00)
        scene.rect(*self.cloud.frame)
        self.root_layer.update(self.dt)
        self.root_layer.draw()

    def touch_began(self, touch):
        self.setup()

MyScene()
