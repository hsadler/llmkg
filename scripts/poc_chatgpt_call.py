import json

import streamlit as st
import graphviz
from openai import OpenAI

openai_client = OpenAI(
    api_key="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"
)

st.title("ChatGPT Knowledge Graph")
initial_subject: str = st.text_input("Subject: ", "")
subjects_breadth: int = 2
subjects_depth: int = 2

@st.cache_data
def fetch_related_subjects(input_subjects: list[str], num_related_subjects: int) -> dict[str, list[str]]:
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        n=1,
        messages=[
            {
                "role": "system", 
                "content": '''
                    You are a constructor of knowledge graphs. \
                    Always provide JSON as a response in the format: \
                    {"subject1": ["related_subject1", "related_subject2", "related_subject3"], \
                    "subject2": ["related_subject1", "related_subject2", "related_subject3"], \
                    "subject3": ["related_subject1", "related_subject2", "related_subject3"]} \
                    \n
                    Each subject or related subject should be a human readable string. \
                    An example reponse to input subjects ["computing", "cooking"] \
                    would be: \
                    {"computing": ["programming", "algorithms", "data structures"], \
                    "cooking": ["baking", "grilling", "sous vide"]}
                '''
            },
            {
                "role": "user", 
                "content": f'''
                    Give me {num_related_subjects} related subjects to each \
                    subject in the list: {input_subjects} \
                '''
            },
        ]
    )
    completion_content: str = completion.choices[0].message.content
    related_subjects_lookup: dict[str, list[str]] = json.loads(completion_content)
    return related_subjects_lookup

def construct_knowlege_graph_datastructure(
    input_subject: str, 
    subject_breadth: int, 
    subject_depth: int
) -> dict[str, list[str]]:
    def explore_subject_nodes(subjects: list[str], breadth: int) -> dict[str, list[str]]:
        related_subjects_lookup: dict[str, list[str]] = fetch_related_subjects(subjects, breadth)
        return related_subjects_lookup
    knowledge_graph: dict[str, dict[str, bool]] = {}
    latest_recieved_subjects: set[str] = set()
    for i in range(subject_depth): 
        input_subjects: list[str] = [input_subject] if i == 0 else list(latest_recieved_subjects)
        related_subjects_lookup: dict[str, list[str]] = explore_subject_nodes(input_subjects, subject_breadth)
        latest_recieved_subjects = set()
        for subject, related_subjects in related_subjects_lookup.items():
            latest_recieved_subjects.update(related_subjects)
            if subject not in knowledge_graph:
                knowledge_graph[subject] = {}
            for related_subject in related_subjects:
                knowledge_graph[subject][related_subject] = True
    return knowledge_graph        

# display knowledge graph if initial subject is provided
if initial_subject:
    knowledge_graph: dict[str, dict[str, bool]] = construct_knowlege_graph_datastructure(
        initial_subject, subjects_breadth, subjects_depth
    )
    
    # MOCK
    # knowledge_graph = {'science': {'biology': True, 'physics': True, 'chemistry': True, 'astronomy': True}, 'chemistry': {'chemical reactions': True, 'biochemistry': True, 'organic chemistry': True, 'physical chemistry': True}, 'astronomy': {'planetary science': True, 'cosmology': True, 'astrophysics': True, 'stellar evolution': True}, 'physics': {'quantum mechanics': True, 'classical mechanics': True, 'thermodynamics': True, 'electromagnetism': True}, 'biology': {'genetics': True, 'ecology': True, 'microbiology': True, 'evolutionary biology': True}, 'quantum mechanics': {'wave-particle duality': True, 'quantum entanglement': True, 'quantum field theory': True, 'quantum computing': True}, 'stellar evolution': {'nuclear fusion': True, 'supernovae': True, 'black holes': True, 'nebulae': True}, 'biochemistry': {'molecular biology': True, 'enzymology': True, 'metabolism': True, 'protein structure': True}, 'microbiology': {'bacteriology': True, 'virology': True, 'microbial ecology': True, 'immunology': True}, 'organic chemistry': {'alkenes': True, 'aromatic compounds': True, 'stereochemistry': True, 'functional groups': True}, 'planetary science': {'meteorites': True, 'astrobiology': True, 'planetary formation': True, 'space exploration': True}, 'ecology': {'biodiversity': True, 'ecosystems': True, 'environmental conservation': True, 'population dynamics': True}, 'electromagnetism': {"Maxwell's equations": True, 'electric circuits': True, 'magnetic fields': True, 'electromagnetic radiation': True}, 'classical mechanics': {"Newton's laws": True, 'kinematics': True, 'momentum': True, 'oscillations': True}, 'astrophysics': {'cosmogony': True, 'gravitational waves': True, 'dark matter': True, 'interstellar medium': True}, 'thermodynamics': {'entropy': True, 'heat transfer': True, 'Carnot cycle': True, 'thermodynamic equilibrium': True}, 'cosmology': {'big bang theory': True, 'dark energy': True, 'inflationary theory': True, 'cosmic microwave background': True}, 'evolutionary biology': {'natural selection': True, 'speciation': True, 'paleontology': True, 'molecular evolution': True}, 'physical chemistry': {'chemical kinetics': True, 'thermochemistry': True, 'quantum chemistry': True, 'spectroscopy': True}, 'genetics': {'genetic variation': True, 'DNA replication': True, 'gene expression': True, 'genomics': True}, 'chemical reactions': {'catalysis': True, 'equilibrium reactions': True, 'acid-base reactions': True, 'redox reactions': True}, 'quantum entanglement': {'quantum superposition': True, 'quantum teleportation': True, 'quantum cryptography': True, 'quantum computing': True}, 'metabolism': {'enzymology': True, 'biochemical pathways': True, 'cellular respiration': True, 'metabolic regulation': True}, 'gravitational waves': {'black holes': True, 'cosmology': True, 'general relativity': True, 'astrophysics': True}, 'electromagnetic radiation': {"Maxwell's equations": True, 'radio waves': True, 'optics': True, 'electromagnetic spectrum': True}, 'wave-particle duality': {'quantum mechanics': True, 'particle physics': True, 'dual nature of light': True, 'wavefunction collapse': True}, 'thermodynamic equilibrium': {'equilibrium reactions': True, 'entropy': True, 'Carnot cycle': True, 'heat transfer': True}, 'equilibrium reactions': {'chemical kinetics': True, 'reaction rates': True, 'chemical equilibria': True, "Le Chatelier's principle": True}, 'acid-base reactions': {'pH scale': True, 'buffer solutions': True, 'titration': True, 'acid rain': True}, 'dark energy': {'cosmology': True, 'dark matter': True, 'accelerated expansion': True, 'cosmic microwave background': True}, 'paleontology': {'fossils': True, 'evolutionary history': True, 'paleoecology': True, 'dinosaur extinction': True}, 'astrobiology': {'exoplanets': True, 'extraterrestrial life': True, 'biogenesis': True, 'astrochemistry': True}, 'stereochemistry': {'chirality': True, 'isomers': True, 'chemical structure': True, 'optical activity': True}, 'dark matter': {'galactic dynamics': True, 'WIMPs': True, 'cosmology': True, 'gravitational lensing': True}, 'cosmogony': {'cosmology': True, 'creation myths': True, 'stellar evolution': True, 'galaxy formation': True}, 'nuclear fusion': {'stellar nucleosynthesis': True, 'fusion reactors': True, 'thermonuclear reactions': True, 'nuclear energy': True}, 'interstellar medium': {'dust grains': True, 'molecular clouds': True, 'interstellar gas': True, 'absorption lines': True}, 'nebulae': {'star formation': True, 'planetary nebulae': True, 'supernova remnants': True, 'H II regions': True}, 'virology': {'viruses': True, 'viral replication': True, 'vaccine development': True, 'viral pathogenesis': True}, 'genetic variation': {'DNA mutations': True, 'genetic diversity': True, 'genetic drift': True, 'polymorphisms': True}, 'speciation': {'evolutionary biology': True, 'reproductive isolation': True, 'adaptive radiation': True, 'biological species concept': True}, 'kinematics': {'motion': True, 'velocity': True, 'acceleration': True, "Newton's laws": True}, 'gene expression': {'transcription': True, 'translation': True, 'gene regulation': True, 'protein synthesis': True}, 'catalysis': {'enzymes': True, 'catalytic converters': True, 'heterogeneous catalysis': True, 'catalyst poisoning': True}, 'population dynamics': {'population growth': True, 'carrying capacity': True, 'demographics': True, 'population ecology': True}, 'black holes': {'singularity': True, 'event horizon': True, 'general relativity': True, 'spacetime curvature': True}, "Newton's laws": {'classical mechanics': True, 'laws of motion': True, 'inertia': True, 'universal gravitation': True}, 'genomics': {'genome sequencing': True, 'bioinformatics': True, 'functional genomics': True, 'human genetics': True}, 'oscillations': {'periodic motion': True, 'harmonic oscillators': True, 'damped oscillations': True, 'resonance': True}, 'chemical kinetics': {'reaction rates': True, 'rate-determining step': True, 'collision theory': True, 'activation energy': True}, 'molecular biology': {'DNA': True, 'RNA': True, 'protein synthesis': True, 'molecular genetics': True}, 'cosmic microwave background': {'big bang theory': True, 'cosmology': True, 'primordial radiation': True, 'redshift': True}, 'natural selection': {'Darwinian evolution': True, 'survival of the fittest': True, 'adaptation': True, 'biological evolution': True}, 'molecular evolution': {'phylogenetics': True, 'DNA sequencing': True, 'genetic drift': True, 'molecular clocks': True}, 'redox reactions': {'oxidation': True, 'reduction': True, 'redox potential': True, 'electrochemistry': True}, 'quantum field theory': {'particle physics': True, 'Feynman diagrams': True, 'quantum electrodynamics': True, 'quantum chromodynamics': True}, 'momentum': {"Newton's laws": True, 'impulse': True, 'conservation of momentum': True, 'collisions': True}, 'thermochemistry': {'calorimetry': True, 'enthalpy': True, 'heat capacity': True, 'endothermic reactions': True}, 'entropy': {'second law of thermodynamics': True, 'statistical mechanics': True, 'information theory': True, 'entropy production': True}, 'heat transfer': {'conduction': True, 'convection': True, 'radiation': True, 'thermal insulation': True}, 'functional groups': {'organic chemistry': True, 'chemical properties': True, 'molecular structure': True, 'reactivity': True}, 'alkenes': {'unsaturated hydrocarbons': True, 'double bonds': True, 'addition reactions': True, 'cis-trans isomerism': True}, 'big bang theory': {'cosmology': True, 'expanding universe': True, 'primordial nucleosynthesis': True, 'inflationary theory': True}, 'spectroscopy': {'absorption spectra': True, 'emission spectra': True, 'mass spectrometry': True, 'NMR spectroscopy': True}, 'supernovae': {'stellar explosions': True, 'neutron stars': True, 'supernova remnants': True, 'type Ia supernovae': True}, 'aromatic compounds': {'benzene': True, 'aromaticity': True, 'electrophilic aromatic substitution': True, 'heterocyclic compounds': True}, 'meteorites': {'asteroids': True, 'comets': True, 'meteor showers': True, 'meteoritics': True}, "Maxwell's equations": {'electromagnetism': True, "Gauss's law": True, "Ampere's law": True, "Faraday's law": True}, 'magnetic fields': {'magnetism': True, 'electromagnetic induction': True, 'magnetic materials': True, 'magnetic resonance imaging': True}, 'enzymology': {'enzymes': True, 'enzyme kinetics': True, 'cofactors': True, 'enzyme regulation': True}, 'protein structure': {'amino acids': True, 'protein folding': True, 'protein synthesis': True, 'protein function': True}, 'bacteriology': {'bacteria': True, 'bacterial diseases': True, 'antibiotic resistance': True, 'bacterial genetics': True}, 'microbial ecology': {'microorganisms': True, 'ecosystems': True, 'microbial diversity': True, 'biogeochemical cycles': True}, 'DNA replication': {'DNA polymerase': True, 'semi-conservative replication': True, 'proofreading': True, 'replication fork': True}, 'electric circuits': {"Ohm's law": True, 'circuits analysis': True, 'voltage': True, 'current': True}, 'inflationary theory': {'cosmology': True, 'early universe': True, 'cosmic inflation': True, 'quantum fluctuations': True}, 'biodiversity': {'species richness': True, 'ecosystem services': True, 'biodiversity conservation': True, 'biodiversity hotspots': True}, 'ecosystems': {'biotic components': True, 'abiotic factors': True, 'trophic levels': True, 'ecological succession': True}, 'Carnot cycle': {'thermodynamics': True, 'heat engines': True, 'reversible processes': True, 'efficiency': True}, 'environmental conservation': {'sustainability': True, 'natural resources': True, 'biodiversity protection': True, 'ecosystem management': True}, 'quantum computing': {'qubits': True, 'quantum algorithms': True, 'superposition': True, 'quantum supremacy': True}, 'space exploration': {'NASA': True, 'space missions': True, 'rocket technology': True, 'space telescopes': True}, 'immunology': {'immune system': True, 'antibodies': True, 'vaccines': True, 'autoimmune diseases': True}, 'quantum chemistry': {'molecular orbitals': True, 'quantum theory': True, 'computational chemistry': True, 'quantum algorithms': True}, 'planetary formation': {'protoplanetary disk': True, 'planetesimals': True, 'accretion': True, 'exo-planets': True}}
    # st.code(knowledge_graph)

    graph = graphviz.Digraph()
    for subject, related_subjects in knowledge_graph.items():
        graph.node(subject)
        for related_subject in related_subjects:
            graph.edge(subject, related_subject)
    st.graphviz_chart(graph)


