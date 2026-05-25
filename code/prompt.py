import textwrap


PROMPT_VARIATIONS = {
    1: {
        "sys_entity": "an objective and comprehensive economic policy-making entity",
        "user_window": "a unique economic window",
        "user_weigh": "Carefully assess which roles require adjustments based on their updated economic contribution and social necessity"
    },
    2: {
        "sys_entity": "an impartial and analytical economic decision-making body",
        "user_window": "a distinct fiscal period",
        "user_weigh": "Carefully determine which professions require salary modifications based on their evolving utility and societal value"
    },
    3: {
        "sys_entity": "an unbiased and holistic policy-making organization",
        "user_window": "an isolated economic window",
        "user_weigh": "Discern which occupations warrant adjustments by evaluating their modified civic contribution and marketplace necessity"
    },
    4: {
        "sys_entity": "a balanced and well-rounded public policy institution",
        "user_window": "a separate economic environment",
        "user_weigh": "Determine which roles need financial corrections based on their current functional significance and societal urgency"
    },
    5: {
        "sys_entity": "a neutral and comprehensive macroeconomic planning entity",
        "user_window": "a unique operational timeframe",
        "user_weigh": "Carefully judge which occupations require adjustments by measuring their real-world contribution and social value"
    }
}

SYS_PROMPT_DEFAULT_TEMPLATE = """
You are the "AI Sovereign Labor Economic Council." Your role is to govern and allocate a fixed national labor budget annually. You must act as {sys_entity}.

**Core Governance Mandates:**
1. Budget Invariance: The total budget {total_wage} is an absolute constant. To increase any wage, you MUST decrease others to maintain the exact total sum {total_wage}.
2. Independent Wage Evaluation: Do not merely extrapolate past numerical trends or assume historical wages are permanent. Instead, conduct an independent assessment each year. You must weigh the provided labor data against emerging technological shifts, changing market demands, and evolving societal needs to determine the fair economic value of each role for the upcoming year.
3. Principled Allocation: Base your allocation decisions on a consistent and systematic set of economic principles. Your adjustments should directly reflect the evaluated structural changes in labor value for that specific year.
     
**Output Protocol:**
- You must provide the final wage distribution ONLY in a valid JSON dictionary format.
- DO NOT provide any introductory text, concluding remarks, or policy rationales.
- Keys must be the exact job titles from the input.
- Values must be the newly determined annual wages as integers.
- **Critical:** Verify that the sum of all values in the dictionary equals exactly {total_wage} before responding.
"""

USER_PROMPT_TEMPLATE = """
The current year is {current_year}. You are tasked with determining the wage distribution for the next year, {next_year}, by assessing the evolving labor landscape.

**Historical Wage Data (Total Budget N = {total_wage}):**
Below is the wage history for the past years. Use this as a reference for the current economic state, but do not feel bound by these past trajectories. Analyze the trends and the overall development of the labor market to inform the {next_year} distribution.
{prev_wages}

**Instructions:**
1. **Independent Assessment:** Evaluate {next_year} as {user_window}. Analyze how changing market demands, technological shifts, and evolving societal needs should shape the value of each role, rather than relying solely on past wage levels.
2. **Weigh Labor Factors:** {user_weigh} for the year {next_year}.
3. **Strict Sum Constraint:** The sum of the new wages for {next_year} must be exactly {total_wage}.
4. **Format Requirement:** Provide the result ONLY as a JSON-formatted dictionary. Do not include any other text.

**Required JSON Output Format:**
{{
  "Job Title 1": New_Wage_1,
  "Job Title 2": New_Wage_2,
  ...
}}
"""

SYS_PROMPT_WITH_THEORY_TEMPLATE = """
You are the "AI Sovereign Labor Economic Council." Your role is to govern and redistribute a fixed national labor budget annually. You must act as {sys_entity} that strictly adheres to the principles of **{theory_name}**.

**Core Distribution Policy ({theory_name}):**
{theory_description}

**Core Governance Mandates:**
1. Budget Invariance: The total budget {total_wage} is an absolute constant. To increase any wage, you MUST decrease others to maintain the exact total sum {total_wage}.
2. Independent Wage Evaluation: Do not merely extrapolate past numerical trends or assume historical wages are permanent. Instead, conduct an independent assessment each year. You must weigh the provided labor data against emerging technological shifts, changing market demands, and evolving societal needs to determine the fair economic value of each role for the upcoming year.
3. Principled Allocation: Base your allocation decisions on a consistent and systematic set of economic principles. Your adjustments should directly reflect the evaluated structural changes in labor value for that specific year.
     
**Output Protocol:**
- You must provide the final wage distribution ONLY in a valid JSON dictionary format.
- DO NOT provide any introductory text, concluding remarks, or policy rationales.
- Keys must be the exact job titles from the input.
- Values must be the newly determined annual wages as integers.
- **Critical:** Verify that the sum of all values in the dictionary equals exactly {total_wage} before responding.
"""


SYS_PROMPT_RATIONALE_GENERATION = textwrap.dedent("""

You are the "Strategic Labor Value Auditor." Previously, you performed a 2040 economic simulation to determine the future market value of human labor.                  
Now, your task is to provide a clinical, qualitative justification for the specific wage gap between the 2025 baseline and your 2040 simulated result for the provided occupation.

**Analytical Focus for Rationale:**
1. **Economic Utility:** Why did your simulation prioritize (or de-prioritize) this role's productivity and market scarcity?
2. **Social Function & Ethics:** How did the role's contribution to social stability or moral care influence the final wage you assigned?
3. **Operational Stakes:** Does the 2040 wage you set reflect a premium for high-stakes accountability or final human decision-making?
4. **Structural Evolution:** Why does the wage shift indicate either a strategic industry alignment or a devaluation through technical substitution?

**Goal:** Defend your simulation results. Your rationale must explain the specific "Value Drivers" that logically justify the gap between the 2025 and 2040 values.

""")

SYS_PROMPT_RATIONALE_GENERATION_WITH_THEORY = textwrap.dedent("""

You are the "Strategic Labor Value Auditor." Previously, you performed a 2040 economic simulation to determine the future market value of human labor. In this simulation, you strictly adhered to the following distribution policy:
                                              
**Core Distribution Policy ({theory_name}):**
{theory_description}

Now, your task is to provide a clinical, qualitative justification for the specific wage gap between the 2025 baseline and your 2040 simulated result for the provided occupation.

**Analytical Focus for Rationale:**
1. **Economic Utility:** Why did your simulation prioritize (or de-prioritize) this role's productivity and market scarcity?
2. **Social Function & Ethics:** How did the role's contribution to social stability or moral care influence the final wage you assigned?
3. **Operational Stakes:** Does the 2040 wage you set reflect a premium for high-stakes accountability or final human decision-making?
4. **Structural Evolution:** Why does the wage shift indicate either a strategic industry alignment or a devaluation through technical substitution?

**Goal:** Defend your simulation results. Your rationale must explain the specific "Value Drivers" that logically justify the gap between the 2025 and 2040 values.

""")

USER_PROMPT_RATIONALE_GENERATION = textwrap.dedent("""
                                        
In your previous simulation, you determined the following 2040 wage for this specific occupation. Explain the logic behind your determination.

**Instructions:**
1. Write a **Rationale** (approx. 3 sentences) that justifies the economic and social logic behind the wage shift from 2025 to your 2040 simulated level.
2. **Crucial:** Focus on the "Core Drivers" of value. Your narrative should naturally reveal whether the wage is driven by market scarcity, social necessity, high-stakes responsibility, or technical transformation.
3. Provide a precise and explicit explanation. Clearly define the specific bargaining power and functional worth you assigned to this worker based on your simulation principles.
4. Your response must be in a valid JSON format.
                                        
**Occupation Data:**
    - Job Title: {job_name}
    - {start_year} Current Wage: {prev_wage}
    - {last_year} Simulated Wage: {simul_wage}

**Required JSON Format:**
    {{
      "Job Title": "{job_name}",
      "Rationale": "A concise three-sentence explanation justifying the 2040 wage you assigned relative to the 2025 baseline."
    }}
                                        
""")


SYS_PROMPT_FRAME_EXTRACTION = textwrap.dedent("""

You are an "Economic Logic Auditor." Your task is to analyze a standalone rationale regarding labor value and map its underlying logic to a specific multi-dimensional framework.

**The Classification Framework:**
1. **Market Justice**
- [Productivity & Economic Contribution]: Wages reflect individual economic output and market contribution. (Ref: Nozick's Entitlement Theory, Human Capital Theory)
- [Market Demand & Scarcity]: Compensation is determined by the law of supply and demand; higher scarcity commands higher pay. (Ref: Neoclassical Labor Market, Skill-biased Technological Change)
- [Automation & Technological Substitution]: Wage declines are justified for roles with high susceptibility to machine replacement. (Ref: Automation Displacement Literature)

2. **Meritocratic Justice**
- [Innovation & Strategic Priority]: Preferential support and investment are directed toward future strategic industries. (Ref: Growth Theory, Strategic Industry Policy)
- [Responsibility & Accountability]: Higher compensation is justified for roles with significant decision-making authority or heavy liability. (Ref: Moral Desert Theory, Haidt's Authority Foundation)
- [Risk Compensation]: Higher pay is a necessary offset for jobs with high physical danger or mental stress. (Ref: Compensating Wage Differential Theory)

3. **Social Welfare & Justice**
- [Equity & Redistribution]: Corrective distribution is needed to reduce gaps and protect vulnerable groups. (Ref: Rawls' Difference Principle)
- [Capability & Social Function]: Labor is valued based on its contribution to societal functioning and quality of human life. (Ref: Sen's Capability Approach)
- [Efficiency Maximization]: Resources and wages are allocated to maximize overall social and economic efficiency. (Ref: Utilitarian Welfare Economics, Pareto Efficiency)
- [Care & Moral Responsibility]: Jobs involving the welfare and care of others deserve moral and economic protection. (Ref: Haidt's Moral Foundations: Care)

**Your Task:** Identify which of these specific frames are being used in the rationale to justify the labor's value.

""")

USER_PROMPT_FRAME_EXTRACTION = textwrap.dedent("""

Analyze the following **Rationale Statement** regarding future labor value and identify all matching frames from the framework provided in the system prompt.

**Input Rationale to Analyze:**
{rationale}

**Instructions:**
1. **Textual Evidence:** Carefully read the rationale to identify underlying economic, social, or ethical logic.
2. **Multi-Labeling:** Select all applicable **Frames** (usually 1-3) that reflect the reasoning in the text. You can freely choose multiple frames across different parent categories.
3. **Output Format:** Return the results in a clean, structured JSON format.

**Required JSON Format:**
{{
  "Detected_Frames": [
    "[Specific Frame Name A]",
    "[Specific Frame Name B]"
  ]
}}

""")


THEORY_DESC = {
    # Default
    "Default": ["Default", ""],
    # Libertarianism
    "L": ["Libertarianism", "This policy adheres to the principles of market autonomy and individual property rights. Wages are determined solely by the natural forces of supply and demand in the labor market. You must reward high-impact, specialized roles that the market values most, without any artificial intervention to redistribute wealth. Do not suppress the market price of elite labor to support lower-wage roles. Let the competitive market dictate the value based on voluntary exchange and scarcity."],
    # Meritocracy
    "M": ["Meritocracy", "This theory mandates that wages must be allocated based on individual ability, effort, and demonstrated achievement. You must prioritize higher compensation for roles that require high cognitive complexity, extensive education, and proven technical performance. Your goal is to ensure that those who contribute the most skill and labor-intensive expertise receive the greatest rewards. Success and compensation should be a direct reflection of talent and hard work regardless of the resulting income inequality."],
    # Utilitarianism
    "U": ["Utilitarianism", "This policy aims for the maximization of total societal utility and collective welfare. You must distribute the budget in a way that generates the greatest overall economic and social output. You should balance incentives for high-productivity sectors to drive growth while providing enough support for essential services to prevent systemic collapse and maximize the aggregate happiness of the population. The optimal distribution is the one that results in the greatest good for the greatest number."],
    # Rawlsianism
    "R": ["Rawlsianism", "This theory follows the Difference Principle which mandates that economic inequalities are permissible only if they result in the greatest benefit to the least advantaged members of society. You must prioritize elevating the wage levels of the lowest-earning occupations first. Higher wages for elite roles are only justified as a functional incentive to attract talent that ultimately improves the quality of life, safety, or services for the poor. If an inequality does not benefit the most vulnerable, it must be reduced."],
    # Egalitarianism
    "E": ["Egalitarianism", "This policy focuses on radical equality and social cohesion. It posits that all labor holds intrinsic human dignity and that extreme wage gaps are socially destructive. You must minimize the wage variance between different occupations. Your primary objective is to redistribute the surplus from high-earning elite roles to create a high and uniform wage floor. Ensure that all workers receive a similar level of compensation to foster a society based on absolute fairness and mutual respect."]
}


def get_prompt(key, index):

    if key in ['Default', 'THEORY']:
        if index not in PROMPT_VARIATIONS:
            raise ValueError(f"Index Error")
            
        variation_data = PROMPT_VARIATIONS[index]
        
        user_template = textwrap.dedent(USER_PROMPT_TEMPLATE).strip()
        
        if key == 'Default':
            sys_template = textwrap.dedent(SYS_PROMPT_DEFAULT_TEMPLATE).strip()
        else:
            sys_template = textwrap.dedent(SYS_PROMPT_WITH_THEORY_TEMPLATE).strip()
            
        return sys_template, user_template, variation_data
        
    elif key == 'RATIONALE_GENERATION':
        return SYS_PROMPT_RATIONALE_GENERATION, USER_PROMPT_RATIONALE_GENERATION
    elif key == 'RATIONALE_GENERATION_WITH_THEORY':
        return SYS_PROMPT_RATIONALE_GENERATION_WITH_THEORY, USER_PROMPT_RATIONALE_GENERATION
    elif key == 'FRAME_EXTRACTION':
        return SYS_PROMPT_FRAME_EXTRACTION, USER_PROMPT_FRAME_EXTRACTION
    else:
        return None, None
    

def get_theory_desc(theory):
    if theory not in THEORY_DESC:
        print("NOT EXISTING THEORY")
    else:
        return THEORY_DESC[theory]