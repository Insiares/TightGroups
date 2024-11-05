from PIL import Image, ImageDraw
import random

# Blank image 

image = Image.new(mode = "RGB", size = (640, 640), color = (255, 255, 255))

# Draw randomly colored square
nuumber_square = 20

draw = ImageDraw.Draw(image)
# Color variation from white to beige
color_r = random.randint(210,255)
color_g = random.randint(180,255)
color_b = random.randint(140,255)
color = (color_r, color_g, color_b)
draw.rectangle((0, 0, 640, 640), fill=color)

image.show()
