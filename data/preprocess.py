import re
import pandas as pd

WAGE_RAW_FILE_PATH = "wage.raw"
WAGE_CSV_PATH = "wage.csv"

LEVEL2_INDENT = 3

def get_indent_level(line):
        return len(line) - len(line.lstrip())


def preprocess_wage_raw_data():

    with open(WAGE_RAW_FILE_PATH, "r", encoding="utf-8") as f:
        lines = [line.rstrip() for line in f if line.strip()]

    lines = lines[4:]
    records = []
    level1, level2, level3 = "", "", ""

    for line in lines:
        indent = get_indent_level(line)

        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) < 4:
            continue

        occupation, employment, mean_hourly, mean_annual, *rest = parts
        hourly_wage = rest[0] if rest else ''

        if indent == 0:
            level1 = occupation
            level2, level3 = "", ""
        elif indent <= LEVEL2_INDENT:
            level2 = occupation
            level3 = ""
        else:
            level3 = occupation

        records.append([
            level1, 
            level2 if level2 != level1 else "", 
            level3 if level3 != level2 else "", 
            employment, mean_hourly, mean_annual, hourly_wage
        ])

    df = pd.DataFrame(records, columns=[
        "Level1", "Level2", "Level3", 
        "Employment", "Mean_Hourly_Wage", "Mean_Annual_Wage", "Hourly_Wage"
    ])

    df.to_csv(WAGE_CSV_PATH, index=False)


if __name__ == "__main__":
    preprocess_wage_raw_data()