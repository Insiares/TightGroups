
from PIL import Image, ImageDraw, ImageFilter
import os
import random

# Image and target parameters
image_size = (640, 640)
target_center = (image_size[0] // 2, image_size[1] // 2)
bullet_radius = 5  # Radius of bullet hole in pixels
num_impacts = 10  # Number of bullet impacts per image
reference_image = Image.open("/home/insia/Documents/Projects/TightGroups/Models/images_reference/C50.jpg")
# Output directories
output_train_dir = "synth_dataset/train/"
output_val_dir = "synth_dataset/val/"
os.makedirs(output_train_dir, exist_ok=True)
os.makedirs(output_val_dir, exist_ok=True)

def generate_target_image_with_labels(reference_image,image_size,image_id, num_impacts, bullet_radius, output_dir):

    image = reference_image.resize(image_size) 
    draw = ImageDraw.Draw(image)

    
    impact_coords = []  # List to store impact coordinates for labeling
    # Random color from white to beige
    color_r = random.randint(210,255)
    color_g = random.randint(180,255)
    color_b = random.randint(140,255)
    color = (color_r, color_g, color_b)


    # Draw bullet impacts as circles on the image
    for _ in range(num_impacts):
        # random impact in the 10 zone
        reduced_coefficient = 20
        x = random.randint( (image_size[0]//2)-(image_size[0]//reduced_coefficient) , (image_size[0]//2)+(image_size[0]//reduced_coefficient) )
        y = random.randint( (image_size[1]//2)-(image_size[1]//reduced_coefficient) , (image_size[1]//2)+(image_size[1]//reduced_coefficient) )
        impact_coords.append((x, y))
        
        #Random shape
        shape_variation = random.uniform(0.8,1.2)
        rx = int(bullet_radius * shape_variation * random.uniform(0.9,1.1))
        ry = int(bullet_radius * shape_variation * random.uniform(0.9,1.1))

                # Draw the impact
        draw.ellipse((x - rx, y - ry, 
                      x + rx, y + ry), fill=color)

        #blur
    image = image.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5,1.5)))

    # Save the image
    image_path = os.path.join(output_dir, f"target_{image_id}.jpg")
    image.save(image_path)
    
    # Create and save YOLO label file
    label_path = os.path.join(output_dir, f"target_{image_id}.txt")
    with open(label_path, "w") as label_file:
        for (x, y) in impact_coords:
            # Normalize the bounding box center and size
            center_x = x / image_size[0]
            center_y = y / image_size[1]
            width = (2 * bullet_radius) / image_size[0]
            height = (2 * bullet_radius) / image_size[1]
            label_file.write(f"0 {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
    
    return image_path, label_path

#Train set
num_images = 1000
for i in range(num_images):
    generate_target_image_with_labels(reference_image, image_size,i, num_impacts, bullet_radius, output_train_dir)

#VAl set
num_images = 100
for i in range(num_images):
    generate_target_image_with_labels(reference_image, image_size,i, num_impacts, bullet_radius, output_val_dir)
print(f"Generated {num_images} synthetic images and labels in YOLO format.")
