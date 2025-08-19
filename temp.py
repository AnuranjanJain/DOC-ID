from PIL import Image, ImageDraw, ImageFont

def create_id_card(participant_img_path, participant_name):
    # === Editable variables ===
    PARTICIPANT_IMG_SIZE = (203, 204)  # (width, height) of participant image inside green circle
    NAME_FONT_SIZE = 45                # Font size for participant name
    CIRCLE_CENTER_X_RATIO = 0.503        # Horizontal position of green circle center (as ratio of width)
    CIRCLE_CENTER_Y_RATIO = 0.5607       # Vertical position of green circle center (as ratio of height)
    NAME_BELOW_CIRCLE = 50             # Pixels below circle for name
    # ==========================
    # Load your saved template image
    template_path = "image.png"
    template_img = Image.open(template_path)

    # Create a blank FHD canvas
    fhd_width, fhd_height = 1920, 1080
    canvas = Image.new("RGB", (fhd_width, fhd_height), (255, 255, 255))

    # Center the template on the canvas, preserving aspect ratio
    template_ratio = template_img.width / template_img.height
    fhd_ratio = fhd_width / fhd_height
    if template_ratio > fhd_ratio:
        # Template is wider than FHD, fit width
        new_width = fhd_width
        new_height = int(fhd_width / template_ratio)
    else:
        # Template is taller than FHD, fit height
        new_height = fhd_height
        new_width = int(fhd_height * template_ratio)
    template_resized = template_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    offset_x = (fhd_width - new_width) // 2
    offset_y = (fhd_height - new_height) // 2
    canvas.paste(template_resized, (offset_x, offset_y))

    # Load and crop participant image to square before resizing
    participant_img = Image.open(participant_img_path)
    min_side = min(participant_img.width, participant_img.height)
    left = (participant_img.width - min_side) // 2
    top = (participant_img.height - min_side) // 2
    right = left + min_side
    bottom = top + min_side
    participant_img = participant_img.crop((left, top, right, bottom))
    participant_img = participant_img.resize(PARTICIPANT_IMG_SIZE)

    # Create circular mask
    mask = Image.new('L', PARTICIPANT_IMG_SIZE, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + PARTICIPANT_IMG_SIZE, fill=255)

    # Apply circular mask to participant image
    participant_circled = Image.new('RGBA', PARTICIPANT_IMG_SIZE)
    participant_circled.paste(participant_img, (0, 0), mask=mask)

    # Set green circle position and size based on template
    circle_center_x = int(fhd_width * CIRCLE_CENTER_X_RATIO)
    circle_center_y = int(fhd_height * CIRCLE_CENTER_Y_RATIO)
    circle_radius = PARTICIPANT_IMG_SIZE[0] // 2
    paste_x = circle_center_x - circle_radius
    paste_y = circle_center_y - circle_radius

    # Paste participant image exactly inside the green circle
    canvas.paste(participant_circled, (paste_x, paste_y), participant_circled)

    # Add participant name and role below the circle
    draw_template = ImageDraw.Draw(canvas)
    font_path = 'Open_Sans/static/OpenSans-Regular.ttf'  # Use Open Sans font for participant name
    # Lower font size if name is longer than 16 characters
    if len(participant_name) > 16 and len(participant_name) <= 20:
        name_font_size = max(24, NAME_FONT_SIZE - 15)  # Lower font size, but not too small
    elif len(participant_name) > 20:
        name_font_size = max(23, NAME_FONT_SIZE - 30)  # Lower font size, but not too small
    else:
        name_font_size = NAME_FONT_SIZE
    try:
        font_name = ImageFont.truetype(font_path, name_font_size)
    except Exception:
        font_name = ImageFont.load_default()

    # Center name below the circle
    name_bbox = draw_template.textbbox((0, 0), participant_name, font=font_name)
    name_w = name_bbox[2] - name_bbox[0]
    name_h = name_bbox[3] - name_bbox[1]
    name_x = circle_center_x - name_w // 2
    name_y = paste_y + PARTICIPANT_IMG_SIZE[1] + NAME_BELOW_CIRCLE

    # Draw name with black outline for visibility
    for dx in [-2, 0, 2]:
        for dy in [-2, 0, 2]:
            if dx != 0 or dy != 0:
                draw_template.text((name_x + dx, name_y + dy), participant_name, font=font_name, fill=(0,0,0))
    draw_template.text((name_x, name_y), participant_name, font=font_name, fill=(255,255,255))

    # Save as FHD PNG
    output_path = "id_card_output_fhd.png"
    canvas.save(output_path)
    print("Saved:", output_path)

    # Optional: Convert to PDF
    pdf_img = Image.open(output_path)
    pdf_img = pdf_img.convert("RGB")
    pdf_img.save("id_card.pdf")
    print("PDF saved: id_card_output_fhd.pdf")

def merge_id_card_with_back(front_path="id_card_output_fhd.png", back_path="back.png", output_path="merged_id_card.png"):
    """
    Merge the front ID card and back image side-by-side into a single image.
    """
    front = Image.open(front_path)
    back = Image.open(back_path)
    # Resize back to match front size, preserving aspect ratio and letterboxing
    target_size = front.size
    back_ratio = back.width / back.height
    target_ratio = target_size[0] / target_size[1]
    if back_ratio > target_ratio:
        # Back is wider, fit width
        new_width = target_size[0]
        new_height = int(new_width / back_ratio)
    else:
        # Back is taller, fit height
        new_height = target_size[1]
        new_width = int(new_height * back_ratio)
    back_resized = back.resize((new_width, new_height), Image.Resampling.LANCZOS)
    # Create a blank canvas and paste back_resized centered
    back_canvas = Image.new("RGB", target_size, (255, 255, 255))
    offset_x = (target_size[0] - new_width) // 2
    offset_y = (target_size[1] - new_height) // 2
    back_canvas.paste(back_resized, (offset_x, offset_y))
    # Merge side by side, aligned at the top, with white background and no extra space
    merged_width = front.width + back_canvas.width
    merged_height = max(front.height, back_canvas.height)
    merged = Image.new("RGB", (merged_width, merged_height), (255, 255, 255))
    merged.paste(front, (0, 0))
    merged.paste(back_canvas, (front.width, 0))
    merged.save(output_path)
    print(f"Merged image saved as {output_path}")

if __name__ == "__main__":
    # Example usage (replace with your actual participant image and name)
    create_id_card("participant.png", "Rosie")
    merge_id_card_with_back()

