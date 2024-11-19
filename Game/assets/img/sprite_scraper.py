from PIL import Image
import numpy as np


# Helper function to check if a pixel is background color
def is_background_color(background_color, pixel):
    return pixel == background_color


def is_not_surrounded_by_background(x0, y0, x1, y1, bg_color, pixels):
    coordinates = [x0, y0, x1, y1]
    for x in range(x0, x1):
        if not is_background_color(bg_color, pixels[x, y0 - 1]):
            coordinates[1] = coordinates[1] - 1
            return coordinates
        if not is_background_color(bg_color, pixels[x, y1 + 1]):
            coordinates[3] = coordinates[3] + 1
            return coordinates
    for y in range(y0, y1):
        if not is_background_color(bg_color, pixels[x0 - 1, y]):
            coordinates[0] = coordinates[0] - 1
            return coordinates
        if not is_background_color(bg_color, pixels[x1 + 1, y]):
            coordinates[2] = coordinates[2] + 1
            return coordinates
    return []


def to_image(x, y, width, height, name, pixels):
    data = []
    for y1 in range(y, y + height):
        row = []
        for x1 in range(x, x + width):
            row.append(pixels[x1, y1])
        data.append(row)
    # Example 2D array (you can replace this with your own data)
    array_2d = np.array(data, dtype=np.uint8)  # Ensure dtype is uint8 for image data

    # Convert the 2D array to a Pillow Image
    img = Image.fromarray(array_2d)

    # Save the image
    img.save(name)


def detect_sprites(spritesheet_path, background_color):
    # Open the spritesheet image
    image = Image.open(spritesheet_path)
    image = image.convert("RGBA")
    width, height = image.size

    # Convert the background color to RGBA
    background_color = (*background_color, 255)  # Assuming alpha is 255 for background

    # Get pixel data
    pixels = image.load()



    # List to store sprite data
    sprites = []

    # Scan through the image to find non-background regions
    visited = [[False] * height for _ in range(width)]

    for y in range(height):
        for x in range(width):
            if not is_background_color(background_color, pixels[x, y]) and not visited[x][y]:
                # Found a new sprite
                sprite_x0, sprite_y0 = x, y
                sprite_x1, sprite_y1 = x, y

                # Expand the sprite region to the right and down
                while sprite_x1 < width and not is_background_color(background_color, pixels[sprite_x1, y]):
                    sprite_x1 += 1
                while sprite_y1 < height and not is_background_color(background_color, pixels[x, sprite_y1]):
                    sprite_y1 += 1

                # # Expand the sprite region until it's surrounded by background
                # while (sprite_x0 > 0 and not is_background_color(background_color, pixels[sprite_x0 - 1, sprite_y0])) or \
                #         (sprite_y0 > 0 and not is_background_color(background_color, pixels[sprite_x0, sprite_y0 - 1])):
                #     sprite_x0 -= 1
                #     sprite_y0 -= 1
                #     sprite_x1 += 1
                #     sprite_y1 += 1
                #     print('Here')
                #     if sprite_x0 <= 0 or sprite_y0 <= 0:
                #         break

                # Store the sprite's bounding box
                sprite = [sprite_x0, sprite_y0, sprite_x1, sprite_y1]
                is_not = is_not_surrounded_by_background(sprite[0], sprite[1], sprite[2], sprite[3], background_color, pixels)
                while is_not != []:
                    sprite = is_not
                    is_not = is_not_surrounded_by_background(sprite[0], sprite[1], sprite[2], sprite[3],
                                                             background_color, pixels)
                # Mark the region as visited
                for xi in range(sprite[0], sprite[2] + 1):
                    for yi in range(sprite[1], sprite[3] + 1):
                        visited[xi][yi] = True

                im = len(sprites)  # Image Id
                print(sprite, end=' ')
                sprites.append([sprite[0], sprite[1], sprite[2] - sprite[0] + 1, sprite[3] - sprite[1] + 1])
                x_, y_, width_, height_ = sprites[im][0], sprites[im][1], sprites[im][2], sprites[im][3]
                image_name = f'./sprites/{im}_{x_}_{y_}_{width_}_{height_}.png'
                to_image(x_, y_, width_, height_, image_name, pixels)
                print(sprites[im], im)

    return sprites

def detect_sprites_in_range(topleft, bottomright, spritesheet_path, background_color):
    # Open the spritesheet image
    image = Image.open(spritesheet_path)
    image = image.convert("RGBA")
    width, height = image.size

    # Convert the background color to RGBA
    background_color = (*background_color, 255)  # Assuming alpha is 255 for background

    # Get pixel data
    pixels = image.load()

    # List to store sprite data
    sprites = []

    # Scan through the image to find non-background regions
    visited = [[False] * height for _ in range(width)]

    for y in range(topleft[1], bottomright[1] + 1):
        for x in range(topleft[0], bottomright[0] + 1):
            if not is_background_color(background_color, pixels[x, y]) and not visited[x][y]:
                # Found a new sprite
                sprite_x0, sprite_y0 = x, y
                sprite_x1, sprite_y1 = x, y

                # Expand the sprite region to the right and down
                while sprite_x1 < width and not is_background_color(background_color, pixels[sprite_x1, y]):
                    sprite_x1 += 1
                while sprite_y1 < height and not is_background_color(background_color, pixels[x, sprite_y1]):
                    sprite_y1 += 1

                # # Expand the sprite region until it's surrounded by background
                # while (sprite_x0 > 0 and not is_background_color(background_color, pixels[sprite_x0 - 1, sprite_y0])) or \
                #         (sprite_y0 > 0 and not is_background_color(background_color, pixels[sprite_x0, sprite_y0 - 1])):
                #     sprite_x0 -= 1
                #     sprite_y0 -= 1
                #     sprite_x1 += 1
                #     sprite_y1 += 1
                #     if sprite_x0 <= 0 or sprite_y0 <= 0:
                #         break

                # Store the sprite's bounding box
                sprite = [sprite_x0, sprite_y0, sprite_x1, sprite_y1]
                is_not = is_not_surrounded_by_background(sprite[0], sprite[1], sprite[2], sprite[3], background_color,
                                                         pixels)
                while is_not != []:
                    sprite = is_not
                    is_not = is_not_surrounded_by_background(sprite[0], sprite[1], sprite[2], sprite[3],
                                                             background_color, pixels)
                # Mark the region as visited
                for xi in range(sprite[0], sprite[2] + 1):
                    for yi in range(sprite[1], sprite[3] + 1):
                        visited[xi][yi] = True

                im = len(sprites)  # Image Id
                print(sprite, end=' ')
                sprites.append([sprite[0], sprite[1], sprite[2] - sprite[0] + 1, sprite[3] - sprite[1] + 1])
                x_, y_, width_, height_ = sprites[im][0], sprites[im][1], sprites[im][2], sprites[im][3]
                image_name = f'./sprites/R{im}_{x_}_{y_}_{width_}_{height_}.png'
                to_image(x_, y_, width_, height_, image_name, pixels)
                print(sprites[im], im)

    return sprites


def detect_sprite_in_position(position, spritesheet_path, background_color):
    # Open the spritesheet image
    image = Image.open(spritesheet_path)
    image = image.convert("RGBA")
    width, height = image.size

    # Convert the background color to RGBA
    background_color = (*background_color, 255)  # Assuming alpha is 255 for background

    # Get pixel data
    pixels = image.load()

    # List to store sprite data
    sprites = []

    # Scan through the image to find non-background regions
    visited = [[False] * height for _ in range(width)]

    x = position[0]
    y = position[1]
    if not is_background_color(background_color, pixels[x, y]) and not visited[x][y]:
        # Found a new sprite
        sprite_x0, sprite_y0 = x, y
        sprite_x1, sprite_y1 = x, y

        # Expand the sprite region to the right and down
        while sprite_x1 < width and not is_background_color(background_color, pixels[sprite_x1, y]):
            sprite_x1 += 1
        while sprite_y1 < height and not is_background_color(background_color, pixels[x, sprite_y1]):
            sprite_y1 += 1

        # Store the sprite's bounding box
        sprite = [sprite_x0, sprite_y0, sprite_x1, sprite_y1]
        is_not = is_not_surrounded_by_background(sprite[0], sprite[1], sprite[2], sprite[3], background_color,
                                                 pixels)
        while is_not != []:
            sprite = is_not
            is_not = is_not_surrounded_by_background(sprite[0], sprite[1], sprite[2], sprite[3],
                                                     background_color, pixels)
        # Mark the region as visited
        for xi in range(sprite[0], sprite[2] + 1):
            for yi in range(sprite[1], sprite[3] + 1):
                visited[xi][yi] = True

        im = len(sprites)  # Image Id
        print(sprite, end=' ')
        sprites.append([sprite[0], sprite[1], sprite[2] - sprite[0] + 1, sprite[3] - sprite[1] + 1])
        x_, y_, width_, height_ = sprites[im][0], sprites[im][1], sprites[im][2], sprites[im][3]
        image_name = f'./sprites/P{im}_{x_}_{y_}_{width_}_{height_}.png'
        to_image(x_, y_, width_, height_, image_name, pixels)
        print(sprites[im], im)

    return sprites


def is_bg_color_array(spritesheet_path, background_color):
    # Open the spritesheet image
    image = Image.open(spritesheet_path)
    image = image.convert("RGBA")
    width, height = image.size

    # Convert the background color to RGBA
    background_color = (*background_color, 255)  # Assuming alpha is 255 for background

    # Get pixel data
    pixels = image.load()

    # Scan through the image to find non-background regions
    is_bg = [[False] * height for _ in range(width)]

    for y in range(height):
        for x in range(width):
            is_bg[x][y] = is_background_color(background_color, pixels[x, y])
            print('T' if is_bg[x][y] else 'F', end='')
        print()

    return is_bg


# Example usage
if __name__ == "__main__":
    spritesheet_path = "batman_spritesheet - Copy.png"
    background_color = (34, 177, 76)
    #sprites = detect_sprites(spritesheet_path, background_color)
    #sprites = detect_sprite_in_position((23,33), spritesheet_path, background_color)
    sprites = detect_sprites_in_range((20, 1525), (620, 1845), spritesheet_path, background_color)
    #is_bg_color_array('./sprites/31.png', background_color)