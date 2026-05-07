import pandas as pd

df = pd.read_csv('results.csv')

df['date'] = pd.to_datetime(df['date'])

df = df[df['date'].dt.year >= 2000]

def get_result(row):
    if row['home_score'] > row['away_score']:
        return 1   # Home Win
    elif row['home_score'] < row['away_score']:
        return -1  # Away Win
    else:
        return 0   # Draw

df['result'] = df.apply(get_result, axis=1)

print("Cleaned Data Preview:")
print(df[['date', 'home_team', 'away_team', 'result']].head())

df.to_csv('cleaned_results.csv', index=False)