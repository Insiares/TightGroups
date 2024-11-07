from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import os
import random
import numpy as np

# Image and target parameters
image_size = (640, 640)
target_center = (image_size[0] // 2, image_size[1] // 2)
bullet_radius = 5  # may have to randomize it in the futureo
min_group_radius = 30
max_group_radius = 200 # Target is ~ 420 px of width, 300px seems fair, but i should pick a good distribution 
num_impacts = 10  # static
reference_image = Image.open("/home/insia/Documents/Projects/TightGroups/Models/images_reference/C50.jpg")
# Output directories
output_train_dir = "synth_dataset_v2/train/"
output_val_dir = "synth_dataset_v2/val/"
os.makedirs(output_train_dir, exist_ok=True)
os.makedirs(output_val_dir, exist_ok=True)

def generate_image_properties():
    margin = 80
    image_propeties : dict = {
        'overall_brightness' : random.uniform(0.5, 1.5),
        'overall_contrast' : random.uniform(0.5, 1.5),
        'overall_sharpness' : random.uniform(0.5, 1.5),
        'image_rotation' : random.randint(0, 360),
        'image_offset_x' : random.randint(-20, 20),
        'image_offset_y' : random.randint(-20, 20),
        'color_shift' : random.uniform(0.5, 1.5),
        'noise_level' : random.randint(10,30),
        'group_center_x_offset' : random.randint(-50, 50),
        'group_center_y_offset' : random.randint(-50, 50),
        'group_radius' : random.randint(min_group_radius, max_group_radius)
    }
    return image_propeties


def apply_image_properties_step1(image, image_propeties):

    image = image.rotate(image_propeties['image_rotation'])
    image = image.transform(image.size,Image.AFFINE, (1,0, image_propeties['image_offset_x'], 0, 1, image_propeties['image_offset_y']))
    return image

def apply_image_properties_step2(image, image_propeties):

    image = ImageEnhance.Sharpness(image).enhance(image_propeties['overall_sharpness'])
    image = ImageEnhance.Contrast(image).enhance(image_propeties['overall_contrast'])
    image = ImageEnhance.Brightness(image).enhance(image_propeties['overall_brightness'])

    image = ImageEnhance.Color(image).enhance(image_propeties['color_shift'])
    image_array = np.array(image)
    noise = np.random.randint(-image_propeties['noise_level'], image_propeties['noise_level'], image_array.shape)
    noisy_image = np.clip(image_array + noise, 0, 255).astype(np.uint8)
    image = Image.fromarray(noisy_image)

    image = image.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5,1.5)))

    return image

def random_impact_position(group_center, max_group_radius):
    angle = random.uniform(0, 2 * np.pi)
    radius = random.uniform(0, max_group_radius)
    x = int(group_center[0] + radius * np.cos(angle))
    y = int(group_center[1] + radius * np.sin(angle))
    return (x, y)

def clip_position(position, image_size, bullet_radius):
    x,y = position
    x = max (bullet_radius, min(x, image_size[0] - bullet_radius))
    y = max (bullet_radius, min(y, image_size[1] - bullet_radius))
    return (x,y)


def generate_target_image_with_labels(reference_image,image_size,image_id, num_impacts, bullet_radius, output_dir):

    image = reference_image.resize(image_size) 

    image_properties = generate_image_properties()

    image = apply_image_properties_step1(image, image_properties)

    draw = ImageDraw.Draw(image)
    group_center = (target_center[0] + image_properties['group_center_x_offset'],
                    target_center[1] + image_properties['group_center_y_offset'])
    impact_coords = []           
    color_r = random.randint(210,255)

    color_g = random.randint(180,255)
    color_b = random.randint(140,255)
    color = (color_r, color_g, color_b)


    # Draw bullet impacts as circles on the image
    for _ in range(num_impacts):

        impact_position = random_impact_position(group_center, image_properties['group_radius'])
        x,y = clip_position(impact_position, image_size, bullet_radius)
        impact_coords.append((x,y))
        
        #Random shape
        shape_variation = random.uniform(0.8,1.2)
        rx = int(bullet_radius * shape_variation * random.uniform(0.9,1.1))
        ry = int(bullet_radius * shape_variation * random.uniform(0.9,1.1))

                # Draw the impact
        draw.ellipse((x - rx, y - ry, 
                      x + rx, y + ry), fill=color)

        #blur

    image = apply_image_properties_step2(image, image_properties)
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
num_images = 5000
for i in range(num_images):
    generate_target_image_with_labels(reference_image, image_size,i, num_impacts, bullet_radius, output_train_dir)

#VAl set
num_images = 500
for i in range(num_images):
    generate_target_image_with_labels(reference_image, image_size,i, num_impacts, bullet_radius, output_val_dir)
print(f"Generated {num_images} synthetic images and labels in YOLO format.")
