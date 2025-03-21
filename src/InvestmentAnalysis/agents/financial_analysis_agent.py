import os
from dotenv import load_dotenv
from textwrap import dedent
import yaml
import pathlib
import streamlit as st

from agno.agent import Agent
from agno.models.google import Gemini
import google.generativeai as genai

from tools.financial_analysis_tools import FinancialAnalysisTools

# Load environment variables and configure Gemini
if os.environ.get("STREAMLIT_CLOUD"):
    # when deploying to streamlit, read from st.secrets
    os.environ["GOOGLE_API_KEY"] = st.secrets("GOOGLE_API_KEY")
else:
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# # load API keys from .env file
# load_dotenv()
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

config_file_path = pathlib.Path(__file__).parent.parent / "config/prompts.yaml"
assert (
    config_file_path.exists()
), f"FATAL ERROR: configuration file {config_file_path} does not exist!"

# load prompts from config/prompts.yaml
# externalizing the prompts from code.
config = None
with open(str(config_file_path), "r") as f:
    config = yaml.safe_load(f)

if config is None:
    raise RuntimeError(
        f"FATAL ERROR: unable to read from configuration file at {config_file_path}"
    )


fa_agent = Agent(
    name="Financial Analysis Agent",
    model=Gemini(id="gemini-2.0-flash"),
    tools=[FinancialAnalysisTools(enable_all=True)],
    goal=dedent(
        """
        Analyse the financial ratios of a company and come up with a recommendation
        of the long term investment potential of the company, with reasons for the same.
    """
    ),
    description=dedent(config["prompts"]["system_prompt"]),
    instructions=dedent(config["prompts"]["financial_analysis_prompt"]),
    expected_output=dedent(config["prompts"]["expected_output_format"]),
    markdown=True,
    # show_tool_calls=True,
    debug_mode=True,
)
