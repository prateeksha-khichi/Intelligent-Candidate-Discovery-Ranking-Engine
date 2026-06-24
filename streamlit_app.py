import streamlit as st
import subprocess
import pandas as pd
import os
import json
import time

st.set_page_config(page_title="Redrob Ranker Sandbox", layout="wide")

st.title("Redrob Candidate Ranker - Sandbox")
st.markdown("""
This is a hosted sandbox for the Redrob Candidate Discovery & Ranking Engine.
It runs the offline ranking pipeline on a small 50-candidate sample to demonstrate the logic.
""")

if st.button("Run Ranker on Sample"):
    with st.spinner("Running ranking pipeline..."):
        start_time = time.time()
        
        # We run the ranker in sample mode. It prints to stdout.
        # But wait, to show it nicely, we can just run it and capture the output.
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.abspath(".")
        
        result = subprocess.run(
            ["python", "-m", "src.ranking.rank_candidates", "--sample"],
            capture_output=True,
            text=True,
            env=env
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            st.success(f"Ranking completed in {elapsed:.2f} seconds!")
            st.markdown("### Top Candidates (Sample Pool)")
            st.text(result.stdout)
        else:
            st.error("Pipeline failed!")
            st.text(result.stderr)
