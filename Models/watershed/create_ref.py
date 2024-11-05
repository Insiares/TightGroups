
from PIL import Image, ImageDraw
import numpy as np

# Reference image
# Load the image
image_ref = Image.open('./images_reference/C50.jpg')
image = Image.open('./images_reference/C50.jpg')
# Create a drawing object
draw = ImageDraw.Draw(image)
draw_ref = ImageDraw.Draw(image_ref)

# Get image dimensions
width, height = image.size

#draw Reference circle
circle_radius = 5 
circle_center = (width / 2, height / 2)
draw_ref.ellipse((circle_center[0] - circle_radius,
    circle_center[1] - circle_radius,
    circle_center[0] + circle_radius,
    circle_center[1] + circle_radius),
    fill='white')
image_ref.save('./images_synth/image_with_circle_ref.jpg')


number_of_synth_images = 10
for i in range(number_of_synth_images):

# random position of new circle center 
    x = np.random.randint(0, width)
    y = np.random.randint(0, height)
# Define circle parameters
    circle_radius = 5  # Adjust size as needed
    circle_center = (x, y)

# Draw the white circle
    draw.ellipse((circle_center[0] - circle_radius, 
                  circle_center[1] - circle_radius, 
                  circle_center[0] + circle_radius, 
                  circle_center[1] + circle_radius), 
                  fill='white')

# Save the modified image
    image.save(f'image_with_circle_{str(i)}.jpg')

# Show the image (optional)
image.show()
