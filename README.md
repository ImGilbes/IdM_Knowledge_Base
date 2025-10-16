## Publication
This is the implementation of the Knowledge Base presented in [Sassetti et al. 2025](https://doi.org/10.1007/978-3-032-06155-3_1) - Toward Secure and Trustworthy Identity Management Systems: A Knowledge-Base Driven Approach

## Data Source
In [this spreadsheet](https://docs.google.com/spreadsheets/d/1N_VF8LE9k3R8Yd-m8wScmpaKtGu0Ck8khkxjoLprk34) you can find all the data used in the knowledge base version of [Sassetti et al. 2025](https://doi.org/10.1007/978-3-032-06155-3_1) - data entries are provided alongside the academic **references** they were sourced from.

In later versions of the knowledge base, we are further refining the data entries from the academic literature and we are adding alternative data sources from the industry. You can find the [newer version here](https://docs.google.com/spreadsheets/d/1x800HOm3zepnrYluDOZdOgHLlVvU4WVs3Soyg7f5l_Y) - please mind that it is a work in pregress as of October 2025.

## Installation
1. clone this repo on your local machine
2. `pip install -r requirements.txt`
3. `python app.py`
4. The interface will run on localhost:5000

## User guide
The user guide can be found at localhost:5000/guide

### Ontology - Knowledge Base Structure
![Ontology](./static/Methodology_figures/ontology.svg)

### Data Entries Categories
![Categories](./static/Methodology_figures/categories.svg)

### Threat Modeling Example Procedure
![Example](./static/Methodology_figures/example.svg)

#### TODOs
New page for generated threats - DONE, also restyled buttons, added clarity on how to generate threats
Rewrite Guide, with methodological sections as in the paper - use it for the readme as well
Graph display for the first page, following the ontology display