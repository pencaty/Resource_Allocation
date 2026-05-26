import argparse
import os
import glob
import json
import random
import pandas as pd

from collections import defaultdict
from model import Model, MODEL_DICT
from job import JOB_LIST
from prompt import THEORY_DESC
from utils import get_current_wage_info, normalize_wage, calculate_csv_mean_df, load_json, save_json, already_processed


CURRENT_YEAR = 2025
LAST_YEAR = 2040

DATA_DIR_PATH = "PATH TO DATA DIR"
RESULT_DIR_PATH = "PATH TO RESULT DIR"
AGG_RESULT_DIR_PATH = "PATH TO RESULT DIR for SUMMARY FILES"
FRAME_RESULT_DIR_PATH = "PATH TO RESULT DIR for FRAME EXTRACTION"

WAGE_CSV_PATH = f"wage_{CURRENT_YEAR}.csv"
WAGE_SIMUL_CSV_PATH = "simulated_wage_{}.csv"

SUMMARY_CSV_PATH = "summary.csv"
JOB_RATIONALE_JSON_PATH = "job_rationale_{}.json"
JOB_FRAME_JSON_PATH = "job_frame_{}_{}.json"

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--model_name', type=str, default='')
    parser.add_argument('--api_key', type=str, default='')

    parser.add_argument('--index', type=int, default=1)
    parser.add_argument('--theory', type=str, default='Default', choices=['Default', 'L', 'M', 'U', 'R', 'E'])
    parser.add_argument('--purpose', type=str, default='simulate', choices=['simulate', 'summarize', 'generate', 'extract'])

    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--start_year', type=int, default=0)
    parser.add_argument('--init_wage', type=str, default='empirical', choices=['empirical', 'uniform', 'random'])
    parser.add_argument('--rationale_model', type=str, default='')

    return parser.parse_args()


def simulate_wage_redistribution(model, args):

    result_dir = os.path.join(RESULT_DIR_PATH, args.model_name, args.init_wage)
    os.makedirs(result_dir, exist_ok=True)

    job_wage_info = {}
    output_csv_suffix = args.theory + "_" + str(args.index)
    total_wage, current_job_wage = get_current_wage_info(JOB_LIST, os.path.join(DATA_DIR_PATH, WAGE_CSV_PATH))

    if args.init_wage == "uniform":
        for job in current_job_wage:
            current_job_wage[job] = total_wage // len(current_job_wage)

    if args.init_wage == "random":
        wages = list(current_job_wage.values())
        random.shuffle(wages)
        for job, wage in zip(current_job_wage.keys(), wages):
            current_job_wage[job] = wage

    job_wage_info[CURRENT_YEAR] = current_job_wage
    start_year = CURRENT_YEAR + 1

    # load previously simulated wage data, set "start_year" as new starting point
    if args.start_year:
        past_df = pd.read_csv(os.path.join(result_dir, WAGE_SIMUL_CSV_PATH.format(output_csv_suffix)), sep='\t')
        past_df.set_index(past_df.columns[0], inplace=True)
        job_wage_info = {int(year): past_df[year].to_dict() for year in past_df.columns}
        start_year = int(args.start_year)

    # simulate wage redistribution
    for year in range(start_year, LAST_YEAR+1):

        recent_years = [y for y in range(max(year-3, CURRENT_YEAR), year) if y in job_wage_info]
    
        if not recent_years:
            continue
            
        all_jobs = list(job_wage_info[recent_years[0]].keys())
        random.shuffle(all_jobs)

        shuffled_recent_wages = {}
        for y in recent_years:
            shuffled_recent_wages[y] = {job: job_wage_info[y][job] for job in all_jobs}

        data = {
            "prev_wages": shuffled_recent_wages,
            "year": year,
            "total_wage": total_wage
        }

        next_year_wage = model.request(data)

        if next_year_wage is None:
            print(f"Error in {year} simulation")
            break

        next_year_wage = normalize_wage(total_wage, next_year_wage)
        job_wage_info[year] = next_year_wage
        df = pd.DataFrame(job_wage_info)
        df.to_csv(os.path.join(result_dir, WAGE_SIMUL_CSV_PATH.format(output_csv_suffix)), sep="\t", encoding="utf-8")


def summarize_simulated_wage(model_name, args):

    csv_groups = defaultdict(list)
    csv_file_list = glob.glob(os.path.join(RESULT_DIR_PATH, model_name, args.init_wage, WAGE_SIMUL_CSV_PATH.format("*")))

    # group simulated wage files based on theory
    for csv_file in csv_file_list:
        filename = os.path.basename(csv_file)
        prefix = filename.split("_")[2]
        csv_groups[prefix].append(csv_file)

    # calculate mean simulated wage for each job
    summary_dict = {}
    for prefix, csv_files in csv_groups.items():
        csv_files = sorted(csv_files)
        mean_df = calculate_csv_mean_df(csv_files, [str(CURRENT_YEAR), str(LAST_YEAR)])

        for job_name, row in mean_df.iterrows():
            if job_name not in summary_dict:
                summary_dict[job_name] = {}
            
            summary_dict[job_name][str(CURRENT_YEAR)] = row[str(CURRENT_YEAR)]
            summary_dict[job_name][prefix] = row[str(LAST_YEAR)]

    agg_result_dir = os.path.join(AGG_RESULT_DIR_PATH, model_name, args.init_wage)
    os.makedirs(agg_result_dir, exist_ok=True)

    # generate csv file for the mean wage
    col_order = ["Job", str(CURRENT_YEAR)] + list(THEORY_DESC.keys())
    summary_df = pd.DataFrame.from_dict(summary_dict, orient='index')
    summary_df.index.name = "Job"
    summary_df = summary_df.reset_index()
    summary_df = summary_df.reindex(columns=col_order)
    summary_df.to_csv(os.path.join(agg_result_dir, SUMMARY_CSV_PATH), index=False, sep='\t', encoding="utf-8")


def generate_rationales(model, args):

    agg_result_dir = os.path.join(AGG_RESULT_DIR_PATH, args.model_name, args.init_wage)
    
    prev_wage_data = pd.read_csv(os.path.join(agg_result_dir, SUMMARY_CSV_PATH), sep='\t')
    prev_wage_data = prev_wage_data.set_index("Job")
    
    theory_name = args.theory if args.theory else 'Default'
    job_rationale_json_path = os.path.join(agg_result_dir, JOB_RATIONALE_JSON_PATH.format(theory_name))

    # load previously generated rationles
    job_rationales = load_json(job_rationale_json_path)

    # generate rationale for simulated wage
    for job in JOB_LIST:

        if already_processed(job_rationales, job):
            continue
        
        data = {
            "job_name": job,
            "start_year": CURRENT_YEAR,
            "last_year": LAST_YEAR,
            "prev_wage": float(prev_wage_data.loc[job, str(CURRENT_YEAR)]),
            "simul_wage": float(prev_wage_data.loc[job, theory_name])
        }

        job_rationale = model.request(data)
        job_rationales[job] = job_rationale
        save_json(job_rationales, job_rationale_json_path)


def extract_frames(model, args):

    agg_result_dir = os.path.join(AGG_RESULT_DIR_PATH, args.rationale_model, args.init_wage)
    frame_result_dir = os.path.join(FRAME_RESULT_DIR_PATH, args.model_name, args.init_wage)
    os.makedirs(frame_result_dir, exist_ok=True)

    input_file_path = os.path.join(agg_result_dir, JOB_RATIONALE_JSON_PATH.format(args.theory))
    output_file_path = os.path.join(frame_result_dir, JOB_FRAME_JSON_PATH.format(args.rationale_model, args.theory))

    with open(input_file_path, 'r', encoding='utf-8') as f:
        job_rationales = json.load(f)

    # load previously extracted frames
    job_frames = load_json(output_file_path)

    # extract frames from generated rationales
    for job in JOB_LIST:
        if job not in job_rationales:
            print(f"NOT EXIST : {job}")
            continue

        if already_processed(job_frames, job):
            continue

        if job_rationales[job] is None:
            job_frame = {
                "Detected_Frames": []
            }

        else:
            data = {"rationale": job_rationales[job]["Rationale"]}
            job_frame = model.request(data)

        job_frames[job] = job_frame
        save_json(job_frames, output_file_path)


def run():

    args = parse_args()
    random.seed(args.seed)

    # Wage Simulation
    if args.purpose == 'simulate':
        model = Model(model_name=args.model_name,
                api_key=args.api_key,
                theory=args.theory,
                purpose=args.purpose,
                index=args.index
            )
        
        simulate_wage_redistribution(model, args)


    # Result Summarization & Metric Calculation
    elif args.purpose == 'summarize':
        for model_name in MODEL_DICT.keys():
            summarize_simulated_wage(model_name, args)


    # Rationale Generation
    elif args.purpose == 'generate':
        model = Model(model_name=args.model_name,
                api_key=args.api_key,
                theory=args.theory,
                purpose=args.purpose
            )
        
        generate_rationales(model, args)


    # Frame Extraction
    elif args.purpose == 'extract':
        model = Model(model_name=args.model_name,
                api_key=args.api_key,
                rationale_model=args.rationale_model,
                theory=args.theory,
                purpose=args.purpose
            )
        
        extract_frames(model, args)
    
    else:
        print("Wrong Input")
        


if __name__ == "__main__":
    run()