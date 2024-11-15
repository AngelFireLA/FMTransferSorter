# combine_shortlists.py

import os
import pandas as pd

def combine_shortlists():
    # Folder where the individual shortlist CSV files are located
    shortlist_folder = 'shortlists'  # Change this to your folder name

    # Initialize an empty DataFrame
    combined_df = pd.DataFrame()

    # List of player types and price ranges
    player_types = ['wonderkids', 'squad_players', 'starters']
    price_ranges = ['low', 'mid', 'high']

    # For each player type and price range, read the corresponding CSV file
    for player_type in player_types:
        for price_range in price_ranges:
            filename = f'{player_type}_{price_range}.csv'
            filepath = os.path.join(shortlist_folder, filename)
            if os.path.exists(filepath):
                # Read the CSV file
                df = pd.read_csv(filepath)
                # Add columns for player type and price range
                df['Player_Type'] = player_type
                df['Price_Range'] = price_range
                # Append to the combined DataFrame
                combined_df = pd.concat([combined_df, df], ignore_index=True)
            else:
                print(f'File {filename} not found in {shortlist_folder}')

    # Save the combined DataFrame to a CSV file
    combined_df.to_csv('general_shortlist.csv', index=False)
    print('Combined shortlist saved to general_shortlist.csv')

if __name__ == '__main__':
    combine_shortlists()
