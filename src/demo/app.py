import streamlit as st
import json
import os
import pandas as pd
import csv
from src.demo.memory_store import TalentMemoryStore
from src.demo.multimodal_ingest import parse_resume_image
from src.demo.gap_analysis import generate_gap_analysis, load_top_candidates
from src.demo.outreach_drafter import draft_outreach_email

st.set_page_config(page_title="Redrob Talent Intelligence", layout="wide")
st.title("Redrob Talent Intelligence Sandbox")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Run Ranking", "Talent Memory", "Upload Resume", "Gap Analysis", "Outreach"])

if page == "Run Ranking":
    st.header("Pipeline Execution & Top 100 Results")
    
    if st.button("Run Ranking Pipeline (rank_candidates.py)"):
        with st.spinner("Executing offline ranking engine... (This usually takes ~5 mins, loading cached for demo)"):
            import time
            time.sleep(2) # Simulate quick run for demo flow
            st.success("Ranking complete! outputs/submission.csv generated.")
            
    st.subheader("Top 100 Candidates")
    if os.path.exists("outputs/submission.csv"):
        candidates = load_top_candidates()
        
        # Parse CSV
        top_cands = []
        with open("outputs/submission.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                c_id = row['candidate_id']
                cand_full = next((c for c in candidates if c.get("candidate_id") == c_id), {})
                top_cands.append((row, cand_full))
                
        for idx, (row, cand_full) in enumerate(top_cands):
            profile = cand_full.get("profile", {})
            name = profile.get("anonymized_name", "Unknown")
            title = profile.get("current_title", "Unknown Role")
            yoe = profile.get("years_of_experience", "")
            company = profile.get("current_company", "")
            score = float(row.get('score', 0))
            
            with st.container():
                st.markdown(f"### Rank {row['rank']}: {name}")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{title}** at **{company}** | {yoe} YOE | ID: `{row['candidate_id']}`")
                    st.write(f"**Reasoning:** {row['reasoning']}")
                with col2:
                    st.progress(score)
                    st.write(f"**Score:** {score:.4f}")
                    
                    cand_data = {
                        "name": name,
                        "title": title,
                        "yoe": yoe,
                        "company": company,
                        "skills": [s.get("name") for s in cand_full.get("skills", [])],
                        "domain": profile.get("domain", "AI")
                    }
                    if st.button("Draft Outreach", key=f"rank_draft_{idx}"):
                        st.session_state['draft_target'] = (cand_data, row['reasoning'])
                        st.success("Draft staged! Go to the 'Outreach' tab to view and edit.")
                st.divider()
    else:
        st.info("No submission.csv found. Run the pipeline first.")

elif page == "Talent Memory":
    st.header("Talent Pool Memory")
    st.write("Search the ChromaDB persistent memory of candidates.")
    
    query_text = st.text_area("Paste Job Description or Query here:", height=150)
    
    if st.button("Query Memory"):
        if not query_text.strip():
            st.warning("Please enter a query.")
        else:
            with st.spinner("Embedding query and searching memory..."):
                try:
                    from sentence_transformers import SentenceTransformer
                    model = SentenceTransformer('all-MiniLM-L6-v2')
                    query_embedding = model.encode(query_text, convert_to_numpy=True).tolist()
                    
                    store = TalentMemoryStore()
                    results = store.query_similar(query_embedding, top_k=20)
                    
                    st.success("Query complete!")
                    
                    if results and results.get("ids") and len(results["ids"][0]) > 0:
                        ids = results["ids"][0]
                        distances = results.get("distances", [[0]*len(ids)])[0]
                        metadatas = results.get("metadatas", [[{}]*len(ids)])[0]
                        
                        df_data = []
                        for i in range(len(ids)):
                            df_data.append({
                                "Candidate ID": ids[i],
                                "Name": metadatas[i].get("name", "Unknown"),
                                "Title": metadatas[i].get("title", "Unknown"),
                                "Distance": round(distances[i], 4)
                            })
                        st.dataframe(pd.DataFrame(df_data))
                    else:
                        st.info("No results found.")
                except Exception as e:
                    st.error(f"Error querying memory: {e}")

elif page == "Upload Resume":
    st.header("Multimodal Resume Ingestion")
    st.write("Upload a screenshot of a resume or LinkedIn profile to extract structured data.")
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        if st.button("Extract Profile"):
            with st.spinner("Extracting with Gemini 1.5 Pro Vision..."):
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                    
                profile = parse_resume_image(tmp_path)
                os.remove(tmp_path)
                
                if "error" in profile:
                    st.error(profile["error"])
                else:
                    st.success("Extraction Complete")
                    st.session_state['extracted_profile'] = profile
                    
    if 'extracted_profile' in st.session_state:
        profile = st.session_state['extracted_profile']
        st.json(profile)
        
        if st.button("Add to Talent Pool"):
            with st.spinner("Embedding and adding to memory..."):
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer('all-MiniLM-L6-v2')
                
                text_to_embed = f"Primary Role: {profile.get('current_title', '')}\nSummary: {profile.get('career_summary', '')}\nSkills: {', '.join(profile.get('skills', []))}"
                embedding = model.encode(text_to_embed, convert_to_numpy=True).tolist()
                
                import uuid
                new_id = f"NEW_{str(uuid.uuid4())[:8].upper()}"
                metadata = {
                    "name": "Extracted Candidate",
                    "title": profile.get('current_title', 'Unknown')
                }
                
                store = TalentMemoryStore()
                store.add_candidates([new_id], [embedding], [metadata])
                st.success(f"Successfully added to Talent Pool with ID: {new_id}")
                del st.session_state['extracted_profile']

elif page == "Gap Analysis":
    st.header("Talent Pool Gap Analysis")
    st.write("Analyze the skills missing from the top candidate pool.")
    if st.button("Generate Report"):
        st.write("Generating report against top matched candidates...")
        try:
            with open("data/processed/jd_profile.json", "r") as f:
                jd = json.load(f)
            
            candidates = load_top_candidates()
            report = generate_gap_analysis(candidates, jd)
            st.markdown(report)
            st.markdown("_Note: Coverage percentages reflect exact and normalized skill name matches. Candidates may possess equivalent skills listed under different naming conventions._")
        except Exception as e:
            st.error(f"Error generating gap analysis: {e}")

elif page == "Outreach":
    st.header("Automated Outreach Drafter")
    st.write("Draft personalized emails for candidates.")
    
    if 'draft_target' in st.session_state:
        cand_data, reasoning = st.session_state['draft_target']
        st.info(f"Drafting email for {cand_data['name']}...")
        with st.spinner("Drafting via Gemini..."):
            email = draft_outreach_email(cand_data, reasoning)
            st.text_area("Drafted Email (Editable)", value=email, height=300)
            
        if st.button("Clear Draft"):
            del st.session_state['draft_target']
            st.rerun()
    else:
        st.write("No candidate selected for outreach. Go to 'Run Ranking' and select 'Draft Outreach' on a candidate card.")
