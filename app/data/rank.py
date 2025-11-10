import pandas as pd

# Read the Excel file
df = pd.read_excel('prod_source_scores_normalized.xlsx')

# Sort the dataframe by:
# 1. Product (to group categories together)
# 2. score_norm (descending - highest score gets rank 1)
# 3. score_sum (descending - tiebreaker)
# 4. source_normalized (ascending alphabetically - second tiebreaker)
df_sorted = df.sort_values(
    by=['Product', 'score_norm', 'score_sum', 'source_normalized'],
    ascending=[True, False, False, True]
)

# Assign ranks within each product group (1 to n for each category)
df_sorted['rank'] = df_sorted.groupby('Product').cumcount() + 1

# Save to new Excel file
output_filename = 'prod_source_scores_normalized_ranked.xlsx'
df_sorted.to_excel(output_filename, index=False)

print(f"Ranking completed! Output saved to: {output_filename}")
