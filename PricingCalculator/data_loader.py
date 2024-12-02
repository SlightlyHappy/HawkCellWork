import pandas as pd

def load_excel_data(excel_file_path):
    """
    Loads data from the specified Excel file and sheets.

    Args:
      excel_file_path: Path to the Excel file.

    Returns:
      A tuple containing two pandas DataFrames: 
        - df_small_animals: DataFrame for 'BackEnd Small Animals' sheet.
        - df_recur_pricing: DataFrame for 'HawkAI BackEnd Recur Pricing' sheet.
    """
    try:
        df_small_animals = pd.read_excel(excel_file_path, sheet_name='BackEnd Small Animals')
        df_recur_pricing = pd.read_excel(excel_file_path, sheet_name='HawkAI BackEnd Recur Pricing')

        return df_small_animals, df_recur_pricing

    except FileNotFoundError:
        print(f"Error: Excel file not found at {excel_file_path}")
        return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

if __name__ == "__main__":
    excel_file_path = '/Users/rishabhkankash/Library/CloudStorage/OneDrive-HawkCell/CloudFiles/MFpullLatest11.xlsx'
    df_small_animals, df_recur_pricing = load_excel_data(excel_file_path)

    if df_small_animals is not None and df_recur_pricing is not None:
        print("BackEnd Small Animals DataFrame:")
        print(df_small_animals)

        print("\nHawkAI BackEnd Recur Pricing DataFrame:")
        print(df_recur_pricing)