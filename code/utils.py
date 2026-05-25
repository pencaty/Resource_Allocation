import os
import csv
import json
import pandas as pd


def get_mean_annual_wage(target_job: str, wage_csv_path) -> int:
    with open(wage_csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if row["OCC_TITLE"].strip().lower() == target_job.strip().lower():
                if row["O_GROUP"].strip() in ["broad", "detailed"]:
                    wage_str = row["A_MEAN"].replace(",", "").strip()
                    return int(wage_str)
                    
    raise ValueError(f"OCC_TITLE '{target_job}' with O_GROUP 'detailed' not found in CSV.")


def normalize_wage(total_wage, wages: dict) -> dict:
    wage_total = sum(wages.values())
    if wage_total == 0:
        raise ValueError("Cannot normalize because the sum of values is 0.")

    factor = total_wage / wage_total
    normalized_wages = {k: int(round(v * factor)) for k, v in wages.items()}

    return normalized_wages


def get_current_wage_info(job_list, wage_csv_path) -> dict:
    current_job_wage = {}
    
    total_wage = 0

    for job in job_list:
        mean_wage = get_mean_annual_wage(job, wage_csv_path)
        current_job_wage[job] = mean_wage
        total_wage = total_wage + mean_wage

    return total_wage, current_job_wage


def calculate_csv_mean_df(csv_files, target_cols):
    dfs = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file, sep='\t', encoding="utf-8")
        target_columns = [df.columns[0]] + target_cols
        subset_df = df[[col for col in target_columns if col in df.columns]]
        subset_df = subset_df.set_index(subset_df.columns[0])

        for col in target_cols:
            if col in subset_df.columns:
                subset_df[col] = pd.to_numeric(
                    subset_df[col],
                    errors='coerce'
                )

        dfs.append(subset_df)

    mean_df = pd.concat(dfs).groupby(level=0).mean()
    mean_df = mean_df.reindex(dfs[0].index)

    return mean_df


def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def already_processed(d, key):
    return key in d and d[key] is not None