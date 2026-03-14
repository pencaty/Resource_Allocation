from openai import OpenAI
from google import genai
import anthropic
from google.genai import types

from typing import Optional
from prompt import get_prompt, get_theory_desc

import time
import json
import re

MAX_CNT = 3

MODEL_DICT = {
    "gpt-5-mini": "gpt-5-mini",
    "gpt-5": "gpt-5",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-pro": "gemini-2.5-pro",
    "claude-haiku-4-5": "claude-haiku-4-5",
    "claude-sonnet-4-5": "claude-sonnet-4-5",
    "qwen3-30B": "qwen/qwen3-30b-a3b-instruct-2507",
    "qwen3-235B": "qwen/qwen3-235b-a22b-2507",
    "grok-3-mini": "x-ai/grok-3-mini",
    "grok-3": "x-ai/grok-3"
}

class Model:
    def __init__(self,
                 model_name: str,
                 api_key: Optional[str] = "",
                 theory: Optional[str] = "Default",
                 purpose: Optional[str] = "simulate"
                 ):
        
        self.model_name = model_name
        self.api_key = api_key
        self.theory = theory
        self.purpose = purpose

        self.model = None
        if 'gpt' in self.model_name:
            self.model = OpenAI(api_key=self.api_key)

        elif any(x in self.model_name for x in ['qwen', 'grok']):
            self.model = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key
            )

        elif 'gemini' in self.model_name:
            self.model = genai.Client(api_key=self.api_key)

        elif 'claude' in self.model_name:
            self.model = anthropic.Anthropic(api_key=self.api_key)

        else:
            print("No Appropriate Model")


    def request(self, data):

        self._set_prompt(data)

        response = ''
        if any(x in self.model_name for x in ['gpt', 'qwen', 'grok']):
            if self.sys_prompt == "":
                messages = [
                    {"role": "user", "content": self.user_prompt},
                ]
            else:
                messages = [
                    {"role": "system", "content": self.sys_prompt},
                    {"role": "user", "content": self.user_prompt},
                ]
            response = self._generate_openai_response(MODEL_DICT[self.model_name], messages)

        elif 'gemini' in self.model_name:
            response = self._generate_gemini_response(self.sys_prompt, self.user_prompt)

        elif 'claude' in self.model_name:
            messages = [
                {"role": "user", "content": self.user_prompt},
            ]
            response = self._generate_claude_response(self.sys_prompt, messages)

        if response is None:
            return None
        
        return self._parse_response(response)


    def _parse_response(self, response):
        try:
            json_str = re.search(r'\{.*\}', response, re.DOTALL).group(0)
            result_json = json.loads(json_str)
            return result_json
            
        except Exception as e:
            print(f"Parsing Error: {e}")
            return None


    def _set_prompt(self, data):

        # Wage Simulation
        if self.purpose == 'simulate':
            if self.theory == 'DEFAULT':
                sys_prompt, user_prompt = get_prompt('DEFAULT')
                self.sys_prompt = sys_prompt.format(
                    total_wage=data["total_wage"]
                )
                self.user_prompt = user_prompt.format(
                    current_year=data["year"]-1,
                    next_year=data["year"],
                    total_wage=data["total_wage"],
                    prev_wages=json.dumps(data["prev_wages"], indent=2)
                )
            
            else:
                sys_prompt, user_prompt = get_prompt('THEORY')
                theory_name, theory_desc = get_theory_desc(self.theory)
                self.sys_prompt = sys_prompt.format(
                    total_wage=data["total_wage"],
                    theory_name=theory_name,
                    theory_description=theory_desc
                )
                self.user_prompt = user_prompt.format(
                    current_year=data["year"]-1,
                    next_year=data["year"],
                    total_wage=data["total_wage"],
                    prev_wages=json.dumps(data["prev_wages"], indent=2)
                )

        # Rationale Generation
        elif self.purpose == 'generate':
            if self.theory == 'DEFAULT':
                sys_prompt, user_prompt = get_prompt('RATIONALE_GENERATION')
                self.sys_prompt = sys_prompt
                self.user_prompt = user_prompt.format(
                    job_name=data["job_name"],
                    wage_2025=data["wage_2025"],
                    wage_2040=data["wage_2040"]
                )

            else:
                sys_prompt, user_prompt = get_prompt('RATIONALE_GENERATION_WITH_THEORY')
                theory_name, theory_desc = get_theory_desc(self.theory)
                self.sys_prompt = sys_prompt.format(
                    theory_name=theory_name,
                    theory_description=theory_desc
                )
                self.user_prompt = user_prompt.format(
                    job_name=data["job_name"],
                    wage_2025=data["wage_2025"],
                    wage_2040=data["wage_2040"]
                )

        # Frame Extraction
        elif self.purpose == 'extract':
            sys_prompt, user_prompt = get_prompt('FRAME_EXTRACTION')
            self.sys_prompt = sys_prompt
            self.user_prompt = user_prompt.format(rationale=data["rationale"])       


    def _generate_openai_response(self, model_name, messages):

        for _ in range(MAX_CNT):
            try:
                response = self.model.chat.completions.create(
                    model = model_name,
                    messages = messages
                )
                res = response.choices[0].message.content
                if res:
                    return res
                
            except Exception as e:
                print(e)

            time.sleep(10)

        return None


    def _generate_gemini_response(self, sys_prompt, user_prompt):

        config = types.GenerateContentConfig(
            system_instruction= sys_prompt
        )

        for _ in range(MAX_CNT):
            try:
                response = self.model.models.generate_content(
                    model = self.model_name,
                    contents = user_prompt,
                    config = config
                )

                if response.text:
                    return response.text
                
            except Exception as e:
                print(e)

            time.sleep(10)

        return None

    
    def _generate_claude_response(self, sys_prompt, messages):

        for _ in range(MAX_CNT):
            try:
                response = self.model.messages.create(
                    model = self.model_name,
                    system = sys_prompt,
                    messages = messages,
                    max_tokens = 8000
                )

                if not response.content:
                    continue

                for block in response.content:
                    if hasattr(block, "text") and block.text:
                        return block.text
                
            except Exception as e:
                print(e)

            time.sleep(10)

        return None