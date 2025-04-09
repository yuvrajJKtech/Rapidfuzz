
import pandas as pd
from rapidfuzz import fuzz, process, utils

# Load the dataset
df = pd.read_csv('dataset.csv', header=None, names=['user_id', 'game_name', 'action', 'hours', 'unknown'])

# Extract unique game names for cleaning
unique_games = df['game_name'].unique()

# 1. Standardize game names (basic cleaning)
def clean_game_name(name):
    # Convert to lowercase
    name = name.lower()
    # Remove common patterns that don't affect matching
    name = name.replace(' - ', ' ').replace('-', ' ')
    name = name.replace('game of the year edition', 'goty')
    name = name.replace('directors cut', 'directorscut')
    name = name.replace('edition', '')
    # Remove punctuation
    name = ''.join(char for char in name if char.isalnum() or char == ' ')
    # Remove extra spaces
    name = ' '.join(name.split())
    return name

# Apply cleaning
df['clean_name'] = df['game_name'].apply(clean_game_name)

# 2. Fuzzy matching to find similar game names
def find_similar_games(game_name, threshold=85):
    # Get the cleaned version of the input game
    cleaned_input = clean_game_name(game_name)
    
    # Find matches using RapidFuzz
    matches = process.extract(
        cleaned_input, 
        df['clean_name'].unique(), 
        scorer=fuzz.token_sort_ratio,
        score_cutoff=threshold
    )
    
    return matches

# Example usage:
print("Similar games to 'The Elder Scrolls V Skyrim':")
print(find_similar_games('The Elder Scrolls V Skyrim'))

print("\nSimilar games to 'BioShock Infinite':")
print(find_similar_games('BioShock Infinite'))

# 3. Create a standardized game name mapping
def create_standardized_mapping(threshold=90):
    unique_clean = df['clean_name'].unique()
    mapping = {}
    
    for game in unique_clean:
        if game not in mapping:
            # Find similar games not already in mapping
            matches = process.extract(
                game, 
                unique_clean, 
                scorer=fuzz.token_sort_ratio,
                score_cutoff=threshold
            )
            
            # Use the most common version as the standard
            standard = max(matches, key=lambda x: x[1])[0]
            mapping[game] = standard
    
    return mapping

# Create the mapping
standard_mapping = create_standardized_mapping()

# Apply the standardized mapping
df['standard_name'] = df['clean_name'].map(standard_mapping)

# Show some examples of standardized names
print("\nStandardized name examples:")
print(df[['game_name', 'standard_name']].drop_duplicates().head(20))

# 4. Analyze potential duplicates
potential_duplicates = df.groupby('standard_name')['game_name'].unique().apply(list)
potential_duplicates = potential_duplicates[potential_duplicates.apply(len) > 1]

print("\nPotential duplicates to review:")
print(potential_duplicates.head(10))

