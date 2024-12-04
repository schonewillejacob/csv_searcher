from keyword_parser import KeywordParser

# Test with a sample CSV file
parser = KeywordParser("test.csv")  # Replace 'test.csv' with your file path
parser.load_csv()
results = parser.search("example_keyword")  # Replace with your keyword
print(results)

