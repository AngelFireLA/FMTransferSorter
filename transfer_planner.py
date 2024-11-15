# transfer_planner.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def transfer_planner():
    # Read the general shortlist or specific shortlist
    # You can specify the filename here
    shortlist_filename = 'general_shortlist.csv'  # Change to your shortlist file
    df = pd.read_csv(shortlist_filename)

    # Read the squad data
    squad_filename = 'squad.csv'  # Change to your squad data file
    squad_df = pd.read_csv(squad_filename)

    # Set the mode (1, 2, or 3)
    mode = 3  # Change this to 1, 2, or 3

    # Define the roles we are interested in
    roles = ['afa', 'ifs', 'ama', 'dmd', 'bpdd', 'fba', 'sks']

    # Handle options based on mode
    if mode == 1:
        # Use the ranges you provided

        # Price ranges for each player type
        price_ranges = {
            'wonderkids': {'cheap': 0, 'mid': 25e6, 'expensive': 50e6},
            'squad_players': {'cheap': 0, 'mid': 40e6, 'expensive': 60e6},
            'starters': {'cheap': 0, 'mid': 60e6, 'expensive': 100e6}
        }

        # Ability thresholds
        ability_thresholds = {'squad_player': 14, 'good_player': 15}

        # User-defined position requirements
        position_requirements = {
            'GK': 2,
            'D (C)': 4,
            'D (L)': 2,
            'D (R)': 2,
            'DM': 2,
            'M (C)': 4,
            'AM (L)': 2,
            'AM (R)': 2,
            'AM (C)': 2,
            'ST (C)': 3
        }

        # User-defined weights
        weights = {
            'price': 0.3,           # Lower price is better
            'ability_in_role': 0.5,  # Higher ability is better
            'age': 0.1,             # Younger age is better
            'player_type_priority': 0.2  # Priority based on player type
        }

    elif mode == 2:
        # Assistant chooses the ranges and thresholds based on their own opinion

        # Price ranges for each player type (Assistant's opinion)
        price_ranges = {
            'wonderkids': {'cheap': 0, 'mid': 20e6, 'expensive': 50e6},
            'squad_players': {'cheap': 0, 'mid': 30e6, 'expensive': 70e6},
            'starters': {'cheap': 0, 'mid': 50e6, 'expensive': 100e6}
        }

        # Ability thresholds (Assistant's opinion)
        ability_thresholds = {'squad_player': 13.5, 'good_player': 15}

        # Position requirements determined by the assistant based on your squad
        position_requirements = {
            'GK': 0,  # You have enough goalkeepers
            'D (C)': 1,  # Need one more center-back
            'M (C)': 2,  # Need two central midfielders
            'ST (C)': 1  # Need one striker
        }

        # Weights chosen by the assistant
        weights = {
            'price': 0.25,           # Lower price is better
            'ability_in_role': 0.6,   # Higher ability is better
            'age': 0.15,             # Younger age is better
            'player_type_priority': 0.3  # Priority based on player type
        }

    elif mode == 3:
        # Data calculated from the given data automatically

        # For abilities, we use the squad data to find mean and std
        squad_abilities = squad_df[roles].max(axis=1)
        ability_mean = squad_abilities.mean()
        ability_std = squad_abilities.std()
        ability_thresholds = {
            'squad_player': ability_mean,
            'good_player': ability_mean + ability_std
        }

        # For price ranges, we use the player data
        price_values = df['Transfer Value'].apply(parse_value)
        price_median = price_values.median()
        price_75th = price_values.quantile(0.75)
        price_90th = price_values.quantile(0.90)
        price_ranges = {
            'wonderkids': {'cheap': 0, 'mid': price_median, 'expensive': price_75th},
            'squad_players': {'cheap': 0, 'mid': price_75th, 'expensive': price_90th},
            'starters': {'cheap': 0, 'mid': price_90th, 'expensive': price_values.max()}
        }

        # Automatically determine position requirements based on squad data
        squad_positions = squad_df['Position'].str.split(', ')
        squad_positions = squad_positions.explode()
        squad_position_counts = squad_positions.value_counts()

        # For simplicity, let's assume we need at least 2 players per position
        position_requirements = {}
        for position in df['Position'].unique():
            position = position.strip()
            current_number = squad_position_counts.get(position, 0)
            required_number = max(2 - current_number, 0)
            position_requirements[position] = required_number

        # Weights (default or calculated)
        weights = {
            'price': 0.2,           # Lower price is better
            'ability_in_role': 0.7,  # Higher ability is better
            'age': 0.1,             # Younger age is better
            'player_type_priority': 0.2  # Priority based on player type
        }

    else:
        print('Invalid mode selected.')
        return

    # Compute min and max prices
    prices = df['Transfer Value'].apply(parse_value)
    max_price = prices.max()
    min_price = prices.min()

    # Compute min and max ages
    ages = df['Age']
    max_age = ages.max()
    min_age = ages.min()

    # Count current squad positions
    squad_positions = squad_df['Position'].str.split(', ')
    squad_positions = squad_positions.explode()
    squad_position_counts = squad_positions.value_counts()

    # Compute positions needed
    positions_needed = {}
    for position, required_number in position_requirements.items():
        current_number = squad_position_counts.get(position, 0)
        positions_needed[position] = max(0, required_number - current_number)

    # Compute the score for each player
    scores = []

    for idx, row in df.iterrows():
        player_score = 0

        # Price score
        price = parse_value(row['Transfer Value'])
        price_score = (max_price - price) / (max_price - min_price)  # Normalized between 0 and 1
        player_score += weights['price'] * price_score

        # Ability in role(s)
        ability_in_role = row[roles].max()
        max_ability = 20
        ability_score = ability_in_role / max_ability  # Normalized between 0 and 1
        player_score += weights['ability_in_role'] * ability_score

        # Age
        age = row['Age']
        age_score = (max_age - age) / (max_age - min_age)  # Younger age gives higher score
        player_score += weights['age'] * age_score

        # Position fit
        player_positions = row['Position'].split(', ')
        need_player_in_position = False
        for pos in player_positions:
            pos = pos.strip()
            if positions_needed.get(pos, 0) > 0:
                need_player_in_position = True
                break


        # Player type priority
        player_type = row.get('Player_Type', 'unknown')
        player_type_priority = {'wonderkids': 0.7, 'starters': 1, 'squad_players': 0.7}
        priority_score = player_type_priority.get(player_type, 0.5)
        player_score += weights['player_type_priority'] * priority_score

        scores.append(player_score)

    # Add the scores to the DataFrame
    df['Score'] = scores

    # Sort the DataFrame by Score
    df_sorted = df.sort_values(by='Score', ascending=False)

    # Save the sorted list to a CSV file
    output_filename = 'sorted_transfer_targets.csv'
    df_sorted.to_csv(output_filename, index=False)
    print(f'Sorted transfer targets saved to {output_filename}')

    # Generate plots
    generate_plots(df_sorted)

def parse_value(value_str):
    # Parse the Transfer Value string and return a numeric value in Euros
    if pd.isna(value_str):
        return 0
    if isinstance(value_str, str):
        if 'Not for Sale' in value_str:
            return 200e6  # Assign a high value
        value_str = value_str.replace('€', '').replace('M', 'e6').replace('K', 'e3').replace(',', '').strip()
        if '-' in value_str:
            # It's a range, take the average
            low, high = value_str.split('-')
            low = parse_numeric_value(low)
            high = parse_numeric_value(high)
            return (low + high) / 2
        else:
            # Single value
            return parse_numeric_value(value_str)
    else:
        return value_str

def parse_numeric_value(value_str):
    # Remove non-numeric characters and convert to float
    try:
        value = float(eval(value_str))
        return value
    except:
        return 0

def generate_plots(df):
    # Generate plots and save to files
    import matplotlib.pyplot as plt

    # Histogram of Scores
    plt.figure()
    df['Score'].hist(bins=20)
    plt.title('Histogram of Player Scores')
    plt.xlabel('Score')
    plt.ylabel('Number of Players')
    plt.savefig('score_histogram.png')

    # Scatter plot of Ability vs Price
    plt.figure()
    prices = df['Transfer Value'].apply(parse_value)
    abilities = df[['afa', 'ifs', 'ama', 'dmd', 'bpdd', 'fba', 'sks']].max(axis=1)
    plt.scatter(prices, abilities)
    plt.title('Ability vs Price')
    plt.xlabel('Price (€)')
    plt.ylabel('Ability in Best Role')
    plt.savefig('ability_vs_price.png')

    print('Plots saved to score_histogram.png and ability_vs_price.png')

if __name__ == '__main__':
    transfer_planner()
