def transform_rgb(examples):
    # Transform the images to RGB
    result = [image.convert("RGB") for image in examples["image"]]
    
    # Update the examples dictionary with the converted images
    examples["pixel_values"] = [image for image in result]
    examples["image"] = result
    
    return examples

