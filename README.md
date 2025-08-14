# llmkg
Exploration of using LLMs to create knowledge graphs

## Requirements

- go 1.24+
- python 3.10+
- uv
- docker
- make

## Getting Started

### Running application

Spin up the application
```bash
make up
```

This will start:
- The [API server](http://127.0.0.1:8000/ping) on port `8000`
- PostgreSQL database on port `5433`
- [Adminer](http://127.0.0.1:8080/?pgsql=db&username=user&db=llmkg_db&ns=public)
    database management tool on port `8080`

Spin down the application
```bash
make down
```

## Development

### API commands:

```bash
http POST localhost:8000/subjects data:='{"name": "science"}' kg_version:='1'
http POST localhost:8000/subjects data:='{"name": "biology"}' kg_version:='1'
http POST localhost:8000/subjects data:='{"name": "chemistry"}' kg_version:='1'

http GET "localhost:8000/subjects?name=science&kg_version=1"
http GET "localhost:8000/subjects?name=biology&kg_version=1"
http GET "localhost:8000/subjects?name=chemistry&kg_version=1"

http POST localhost:8000/subject-relations data:='{"subject_id": "4:16987f9f-8033-4cd6-a7c6-94493f1f20ba:15", "related_subject_id": "4:16987f9f-8033-4cd6-a7c6-94493f1f20ba:14"}' kg_version:='1'

# Truncate tables
http POST localhost:8000/truncate-tables
```

### Neo4j queries

```bash
MATCH (s1:Subject {kgVersion: "1"})
OPTIONAL MATCH (s1)-[r:RELATED_TO]-(s2:Subject)
RETURN s1, r, s2
```

## TODO
- [ ] Write cypher queries for Knowledge Graph for gaining insights:
    - [ ] Subjects with the most references as a related subject could be considered as one of the
        most important or general subjects
    - [ ] Calculate the average number of related subjects per subject
    - [ ] Query to find subject clusters
- [ ] Create a few more knowledge graph versions
- [ ] See if the clustering is similar for each KG version
- [ ] Iterate on LLM prompt
    - [ ] Have it only get progressively more specific as it goes deeper
    - [ ] Have it return some parent and some children
    - [ ] Fix bug where subject special characters are not handled correctly
