import os

import streamlit as st
import graphviz
from openai import OpenAI
from dotenv import load_dotenv

from llm_utils import OpenAIModel, SubjectToRelatedSubjects, fetch_related_subjects

load_dotenv()

DEFAULT_SUBJECTS_BREADTH: int = 3
DEFAULT_SUBJECTS_DEPTH: int = 3

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

st.set_page_config(
    page_title="ChatGPT Knowledge Graph",
    page_icon="🧠",
    layout="wide",
)
st.title("ChatGPT Knowledge Graph")

# gather user inputs
initial_subject: str = st.text_input("Subject: ", "")
subjects_breadth: int = st.number_input("Subjects Breadth: ", value=DEFAULT_SUBJECTS_BREADTH)
subjects_depth: int = st.number_input("Subjects Depth: ", value=DEFAULT_SUBJECTS_DEPTH)

def construct_knowlege_graph(
    input_subject: str, 
    subject_breadth: int, 
    subject_depth: int,
) -> dict[str, dict[str, bool]]:
    def explore_subject_nodes(subjects: list[str], breadth: int) -> list[SubjectToRelatedSubjects]:
        related_subjects: list[SubjectToRelatedSubjects] | None = fetch_related_subjects(
            openai_client=openai_client,
            model_name=OpenAIModel.GPT_4_1_NANO.value,
            input_subjects=subjects,
            num_related_subjects=breadth,
        )
        if related_subjects is None:
            raise Exception("Failed to fetch related subjects")
        return related_subjects
    knowledge_graph: dict[str, dict[str, bool]] = {}
    latest_recieved_subjects: set[str] = set()
    for i in range(subject_depth): 
        input_subjects: list[str] = [input_subject] if i == 0 else list(latest_recieved_subjects)
        try:
            related_subjects: list[SubjectToRelatedSubjects] = explore_subject_nodes(input_subjects, subject_breadth)
            print(f"Related subjects lookup: {related_subjects}")
        except Exception as e:
            st.error(f"Error exploring subject nodes: {e}")
            continue
        latest_recieved_subjects = set()
        for subject_to_related_subjects in related_subjects:
            subject_name = subject_to_related_subjects.subject_name.lower()
            related_subject_names = [
                related_subject.lower() for related_subject in subject_to_related_subjects.related_subject_names
            ]
            latest_recieved_subjects.update(related_subject_names)
            if subject_name not in knowledge_graph:
                knowledge_graph[subject_name] = {}
            for related_subject_name in related_subject_names:
                knowledge_graph[subject_name][related_subject_name] = True
    return knowledge_graph        

# display knowledge graph if initial subject is provided
if initial_subject:
    knowledge_graph: dict[str, dict[str, bool]] = construct_knowlege_graph(
        initial_subject, subjects_breadth, subjects_depth
    )

    # Pretty print the knowledge graph data structure
    st.subheader("Knowledge Graph Data Structure")
    st.json(knowledge_graph)

    st.subheader("Knowledge Graph Visualisation")
    graph = graphviz.Digraph(
        name="knowledge_graph",
        format="png", 
        renderer="gd",
        graph_attr={
            "rankdir": "LR",
            "nodesep": "0.5",
            "shape": "box"
        },
        strict=True
    )
    for subject, related_subjects in knowledge_graph.items():
        graph.node(subject)
        for related_subject in related_subjects:
            graph.edge(subject, related_subject)
    st.graphviz_chart(graph, use_container_width=True)
