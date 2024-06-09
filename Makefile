
poc_streamlit:
	poetry run -C streamlit/ streamlit run streamlit/poc_llm_knowledge_graph.py

populate:
	poetry run -C streamlit/ streamlit run streamlit/populate.py
