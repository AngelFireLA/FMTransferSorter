# generate_player_images.py

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os

def generate_player_images():
    # Load the player data
    data_filename = 'general_shortlist.csv'  # Change this if your file has a different name
    df = pd.read_csv(data_filename)

    # Directory to save player images
    output_dir = 'player_images'
    os.makedirs(output_dir, exist_ok=True)

    # Font settings
    title_font = ImageFont.truetype("arial.ttf", size=24)
    text_font = ImageFont.truetype("arial.ttf", size=18)
    small_text_font = ImageFont.truetype("arial.ttf", size=16)

    # Define the mapping from positions to ability columns
    position_ability_mapping = {
        'M/AM (R)': ['ifs'],
        'M/AM (L)': ['ifs'],
        'M (C)': ['ama', 'dmd'],
        'D (C)': ['bpdd'],
        'AM (C)': ['ama'],
        'D (LC)': ['fba'],
        'ST (C)': ['afa'],
        'GK': ['sks'],
        'D (R)': ['fba'],
        'D (L)': ['fba'],
        'AM (L)': ['ifs'],
        'DM': ['dmd'],
        'D/WB (R)': ['fba'],
        'M/AM (C)': ['ama', 'dmd'],
        'AM (LC)': ['ifs'],
        'AM (RL)': ['ifs'],
        'AM (RC)': ['ifs'],
        'AM (R)': ['ifs'],
        'D/WB (L)': ['fba'],
        'D (RC)': ['bpdd', 'fba'],
        'M (R)': ['ifs']
    }

    # Iterate over each player
    for index, row in df.iterrows():
        # Create a new image with white background
        img = Image.new('RGB', (600, 300), color='white')
        draw = ImageDraw.Draw(img)

        # Starting positions for text
        x = 20
        y = 20

        # Player Name
        name = row['Name']
        draw.text((x, y), f"Name: {name}", font=title_font, fill='black')
        y += 40

        # Age and Value
        age = row['Age']
        value = row['Transfer Value']
        draw.text((x, y), f"Age: {age}      Value: {value}", font=text_font, fill='black')
        y += 30

        # Player Type
        player_type = row.get('Player_Type', 'Unknown').capitalize()
        draw.text((x, y), f"Type: {player_type}", font=text_font, fill='black')
        y += 30

        # Positions
        positions = row['Position']
        draw.text((x, y), f"Positions: {positions}", font=text_font, fill='black')
        y += 30

        # Abilities at Positions
        draw.text((x, y), "Abilities at Positions:", font=text_font, fill='black')
        y += 30

        position_list = positions.split(', ')
        displayed_positions = set()

        for pos in position_list:
            pos = pos.strip()
            if pos in position_ability_mapping:
                ability_cols = position_ability_mapping[pos]
                for ability_col in ability_cols:
                    ability_score = row.get(ability_col, None)
                    if pd.notna(ability_score):
                        draw.text((x + 20, y), f"{pos}: {ability_score}", font=small_text_font, fill='black')
                        y += 25
                        displayed_positions.add(pos)
                        break  # Stop after displaying one ability per position
            else:
                # Position not in mapping
                draw.text((x + 20, y), f"{pos}: N/A", font=small_text_font, fill='black')
                y += 25

        # Save the image
        # Replace any illegal characters in the filename
        filename = f"{name.replace('/', '_')}.png"
        filepath = os.path.join(output_dir, filename)
        img.save(filepath)
        print(f"Saved image for {name}")

if __name__ == '__main__':
    generate_player_images()
