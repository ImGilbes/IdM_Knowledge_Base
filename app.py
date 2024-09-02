from flask import Flask, render_template, jsonify, request, redirect, url_for
import pandas as pd
import json

app = Flask(__name__)

CSV_BASE_PATH = 'data/'

CATEGORIES_MAP = {"Conf&DataDiscl":"Confidentiality and Data Disclosure", 
              "Rights":"People Rights", 
              "Adoption": "Adoption",
              "ServiceQuality": "Service Quality",
              "Law&Compliance": "Laws, Regulations, Compliance",
              "Technical": "Technical",
              "Security":"Security",
              "Privacy": "Privacy",
              "Trust": "Trust",
              "SysDesign": "System Design",
              "Governance&Procedures": "Governance Actors, Management, and Procedures",
              "Governance&Procedure": "Governance Actors, Management, and Procedures",
              "Management": "Governance Actors, Management, and Procedures",
              "Socio-political": "Social and Political",
              "Functional": "Functional Requirement",
              "Integr": "Integrity",
              "Avail": "Availability",
              "Transp": "Transparency",
              "Surv": "Surveillance",
              "Authn&Authz": "Authenticity of Data and Identity, Authorization",
              "Abuse": "Abuse of system functionality"
              }

def rename_columns(df):
    global CATEGORIES_MAP
    return df.rename(columns=CATEGORIES_MAP)

SPECIFIC_ENTITY = None
SPECIFIC_DEF = None

def get_categories(df):
    tmp = set(df.columns)
    tmp.discard('Name')
    tmp.discard('Threats')
    tmp.discard('Requirements')
    tmp.discard('Mitigations')
    tmp.discard('Goals')
    return tmp

def cleanup_df(df,entity):
    if entity == "Requirements":
        return df.drop(labels=['References','Description','Addresses'], axis=1)
    elif entity == "Threats":
        return df.drop(labels=['References','Description','Security','Privacy','STRIDE','LINDDUN','Origin'], axis=1)
    elif entity == "Mitigations":
        return df.dropna(axis=1)


def simplify_table(df,entity):
    simplified_df = pd.DataFrame()
    simplified_df[entity] = df[entity]

    categories = get_categories(df)

    df["name_index"] = df[entity]
    df = df.set_index("name_index")
    
    cats = []
    for cur_name in df[entity]:
        tmp = []
        for cat in categories:
            if df.at[cur_name,cat] == 'T':
                tmp.append(cat)
        cats.append(tmp)
    simplified_df["Categories"] = cats

    df = df.reset_index().drop(labels=['name_index'],axis=1)
    # simplified_df = simplified_df.reset_index().set_index("index")
    simplified_df = simplified_df.reset_index().drop(labels=['index'], axis=1)
    return simplified_df

def read_and_cleanup(entity):
    df = pd.read_csv(CSV_BASE_PATH + entity + ".csv")
    df = df.reset_index().set_index("index").reset_index()
    df.drop(labels=['index'], axis=1, inplace=True)
    df = cleanup_df(df,entity)
    return df


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_table', methods=['GET'])
def get_table():
    entity = request.args.get("entity")
    df = rename_columns(read_and_cleanup(entity))

    # if you wanna display only the categories and not the entire table, uncomment either of these
    # df = simplify_table(rename_columns(df),entity)
    # df = simplify_table(df,entity)

    return jsonify(table_html=df.to_html(classes='data-table', index=False, index_names=False))

@app.route('/specific', methods=['GET'])
def specific():
    return render_template('specific.html')

@app.route('/set_specific', methods=['GET'])
def set_specific():
    global SPECIFIC_ENTITY
    global SPECIFIC_DEF 
    SPECIFIC_ENTITY = request.args.get("entity")
    SPECIFIC_DEF = request.args.get("def")
    return "ok"


def build_connections_table(name,definition,conn_entity):
    main_df = read_and_cleanup(name)
    df2 = read_and_cleanup(conn_entity)

    # find specific row in main df
    row = main_df[main_df[name] == definition].reset_index()

    # interesect the categories between the two dfs
    shared_cats = set()
    # extract categories from the extracted row
    for cat in get_categories(main_df).intersection(get_categories(df2)):
        if row.at[0,cat] == 'T':
            shared_cats.add(cat)

    # select all rows in df2 that match the signature of the interesected categories
    mask = pd.Series([True] * len(df2))
    
    for col in shared_cats:
        mask &= df2[col].isin(['T'])

    return (rename_columns(df2[mask]), list(shared_cats))


def rename_shared_cats(shared_cats):
    global CATEGORIES_MAP
    tmp = []
    for cats1 in shared_cats:
        tmp.append([CATEGORIES_MAP.get(c, c) for c in cats1])
    return tmp


@app.route('/get_specific', methods=['GET'])
def get_specific():
    global SPECIFIC_DEF
    global SPECIFIC_ENTITY

    starting_record = None

    connections = {
        "Requirements": ["Mitigations"],
        "Mitigations": ["Requirements","Threats"],
        "Threats": ["Mitigations"]
    }
    
    tables = []
    shared_cats = []  # both tables and shared categories are going to be a list of lists
    if (SPECIFIC_DEF is not None) and (SPECIFIC_ENTITY is not None):

        df = read_and_cleanup(SPECIFIC_ENTITY)
        starting_record = df[df[SPECIFIC_ENTITY] == SPECIFIC_DEF]
        starting_record = rename_columns(starting_record)
        for entity in connections[SPECIFIC_ENTITY]:
            (df, app) = build_connections_table(name=SPECIFIC_ENTITY,definition=SPECIFIC_DEF, conn_entity=entity)
            shared_cats.append(app)
            tables.append(df.to_html(classes='data-table', index=False, index_names=False))

    return jsonify(entity=SPECIFIC_ENTITY,
                    starting_record=starting_record.to_html(classes='data-table', index=False, index_names=False),
                    entities=connections[SPECIFIC_ENTITY],
                    tables=tables,
                    shared_cats=rename_shared_cats(shared_cats))
    

if __name__ == '__main__':
    app.run(debug=True)