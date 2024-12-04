import pandas as pd
from collections import Counter

def parse_csv(file_path):
    """
    Parses a generic CSV file and extracts insights.
    
    :param file_path: Path to the CSV file.
    :return: A tuple of (headers, data rows, insights).
    """
    try:
        # Attempt to load the CSV file with utf-8 encoding
        try:
            data = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            # If utf-8 fails, fallback to ISO-8859-1
            data = pd.read_csv(file_path, encoding='ISO-8859-1')

        # Extract headers and rows
        headers = list(data.columns)
        rows = data.values.tolist()

        # Generate generic insights
        insights = {}

        # 1. Dataset shape
        insights["Shape"] = {"Rows": data.shape[0], "Columns": data.shape[1]}

        # 2. Column-wise insights
        insights["Column Insights"] = {}
        for column in headers:
            if pd.api.types.is_numeric_dtype(data[column]):
                # Numeric column statistics
                insights["Column Insights"][column] = {
                    "Mean": round(data[column].mean(), 2) if not data[column].isnull().all() else None,
                    "Min": data[column].min() if not data[column].isnull().all() else None,
                    "Max": data[column].max() if not data[column].isnull().all() else None,
                    "Unique Values": data[column].nunique(),
                }
            else:
                # Categorical or text column
                top_values = data[column].value_counts().head(5).to_dict()
                insights["Column Insights"][column] = {
                    "Top Values": top_values,
                    "Unique Values": data[column].nunique(),
                }

        # 3. Extract keywords for text columns
        insights["Keywords"] = {}
        for column in headers:
            if pd.api.types.is_string_dtype(data[column]):  # Check for text-based columns
                all_text = " ".join(data[column].dropna().astype(str))
                word_counts = Counter(all_text.split())
                insights["Keywords"][column] = word_counts.most_common(10)

        return headers, rows, insights

    except pd.errors.EmptyDataError:
        print("The file is empty or invalid.")
        return None, None, None
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return None, None, None

