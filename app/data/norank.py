import pandas as pd
import re

# Read the Excel file
df = pd.read_excel('Book1.xlsx')

# Function to extract citations from response text
def extract_citations(response_text):
    """
    Extract citations in the format [1]: https://...
    Returns a string with all citations separated by newlines
    """
    if pd.isna(response_text):
        return ""
    
    # Pattern to match citations like [1]: https://... or [2]: http://...
    citation_pattern = r'\[\d+\]:\s*https?://[^\s]+'
    
    # Find all citations
    citations = re.findall(citation_pattern, str(response_text))
    
    # Join citations with newline
    return '\n'.join(citations) if citations else ""

# Get all unique products that have amazon recommended
products_with_amazon = df[df['source_normalized'] == 'amazon']['product_name'].unique()

# Filter out products that DON'T have amazon
df_no_amazon = df[~df['product_name'].isin(products_with_amazon)]

# For each unique product, get the first response (since all responses for a product should be the same)
df_no_amazon_unique = df_no_amazon.groupby('product_name').first().reset_index()

# Create output dataframe with Product, product_name, and extracted citations
output_df = df_no_amazon_unique[['Product', 'product_name', 'Response']].copy()

# Extract citations from Response column
output_df['Citations'] = output_df['Response'].apply(extract_citations)

# Drop the Response column (not needed in final output)
output_df = output_df[['Product', 'product_name', 'Citations']]

# Rename columns for clarity
output_df.columns = ['Product Category', 'Product Name', 'Citations']

# Sort by Product Category and Product Name
output_df = output_df.sort_values(by=['Product Category', 'Product Name']).reset_index(drop=True)

# Save to Excel
output_filename = 'products_without_amazon_with_citations.xlsx'
output_df.to_excel(output_filename, index=False)

print(f"✓ Output saved to: {output_filename}")
print(f"Total products without Amazon: {len(output_df)}")
