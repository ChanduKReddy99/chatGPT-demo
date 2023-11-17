import os
import json
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)


def extract_financial_data(text):
    prompt = get_prompt_financial() + text
    response = fetch_data_from_openai(prompt)
    try:
        data = json.loads(response)
        return convert_data_to_dataframe(data)
    except (json.JSONDecodeError, IndexError) as e:
        # Handle parsing errors or API response issues
        print(f"Error: {e}")
        return create_empty_dataframe()


def fetch_data_from_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0]["message"]["content"]


def convert_data_to_dataframe(data):
    return pd.DataFrame(data.items(), columns=["Measure", "Value"])


def create_empty_dataframe():
    return pd.DataFrame(
        {
            "Measure": ["Company Name", "Stock Symbol", "Revenue", "Net Income", "EPS"],
            "Value": ["", "", "", "", ""],
        }
    )


def get_prompt_financial():
    return """Please retrieve company name, revenue, net income and earnings per share (a.k.a. EPS)
    from the following news article. If you can't find the information from this article 
    then return "". Do not make things up.    
    Then retrieve a stock symbol corresponding to that company. For this you can use
    your general knowledge (it doesn't have to be from this article). Always return your
    response as a valid JSON string. The format of that string should be this, 
    {
        "Company Name": "Walmart",
        "Stock Symbol": "WMT",
        "Revenue": "12.34 million",
        "Net Income": "34.78 million",
        "EPS": "2.1 $"
    }
    News Article:
    ============
    """


if __name__ == "__main__":
    TEXT = """
    Tesla's Earning news in text format: Tesla's earning this quarter blew all the estimates. They reported 4.5 billion $ profit against a revenue of 30 billion $. Their earnings per share was 2.3 $
    """
    df = extract_financial_data(TEXT)

    print(df.to_string())
