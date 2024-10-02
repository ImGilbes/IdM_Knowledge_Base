from flask import Flask, render_template, jsonify, request, redirect, url_for
import pandas as pd
import json
import numpy as np

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
    match entity:
        case "Requirements":
            # return df.drop(labels=['References','Description'], axis=1)
            return df.drop(labels=['References','Description','OP','RP','Generic'], axis=1)
        case "Threats":
            # return df.drop(labels=['References','Description','Security','Privacy','STRIDE','LINDDUN'], axis=1)
            return df.drop(labels=['References','Description','Security','Privacy','STRIDE','LINDDUN','OP','RP','Generic'], axis=1)
        case "Mitigations":
            return df.drop(labels=['OP','RP','Generic'], axis=1).dropna(axis=1)
        case "Goals":
            # return df.drop(labels=['References','Description'], axis=1)
            return df.drop(labels=['References','Description','OP','RP'], axis=1)
        case "Issues":
            return df.drop(labels=["Description","Ref","Impacts","ORIGIN"], axis=1)
        case "Limitations":
            return df.drop(labels=["Description","Ref","Impacts","ORIGIN"], axis=1)
        case "Attacks":
            return df.drop(labels=["References"], axis=1)
        case "Vulnerabilities":
            return df.drop(labels=["Description","References"], axis=1)
        case _:
            return df

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
    # print(df)
    return df


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/knowledge_base')
def knowledge_base():
    return render_template('knowledge_base.html')

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
    df2 = read_and_cleanup(conn_entity).reset_index().drop(labels=["index"],axis=1)

    # find specific row in main df
    row = main_df[main_df[name] == definition].reset_index()

    # old method for creating connections by matching al the categories to T
    # interesect the categories between the two dfs
    # shared_cats = set()
    # # extract categories from the extracted row
    # for cat in get_categories(main_df).intersection(get_categories(df2)):
    #     if row.at[0,cat] == 'T': # here a weird error occurs, but only for some records
    #         shared_cats.add(cat)

    # # select all rows in df2 that match the signature of the interesected categories
    # mask = pd.Series([True] * len(df2)) 
    # for col in shared_cats:
    #     mask &= df2[col].isin(['T'])

    # return (rename_columns(df2[mask]), list(shared_cats))

    shared_cats = get_categories(main_df).intersection(get_categories(df2))
    # it should be sorted, but i should try
    row_binary = row[list(shared_cats)].replace({'T': 1, 'F': 0})
    df2_binary = df2[list(shared_cats)].replace({'T': 1, 'F': 0})
    empty_df = pd.DataFrame(columns=df2.columns)

    # threshold = 4 / len(shared_cats)

    for index, row in df2_binary.iterrows():

        tmp = pd.DataFrame(row).T

        #EUCLIDEAN DISTANCE METHOD
        # for each row, carry out the distance. If the records are close up to 
        # distance = np.linalg.norm(row_binary - row)
        # if(distance <= 2):
        #     empty_df.loc[len(empty_df)] = df2.iloc[index]
        # print(row_binary, row)

        #COSINE SIMILARITY NORM
        try:
            dot_product = tmp.dot(row_binary.T) # doesnt change if i do this row_binary.dot(tmp.T)
            dot_product = dot_product.iloc[0][0] # this is because a datframe is returned from the operation above
            norm_A = np.linalg.norm(row_binary)
            norm_B = np.linalg.norm(tmp)
            # print(row_binary)
            # print(tmp)
            # print(norm_A)
            # print(norm_B)
            if (norm_A != 0) and (norm_B != 0):
                cosine_similarity = dot_product / (norm_A * norm_B)
            else: 
                cosine_similarity = 0
        except:
            cosine_similarity = 0

        if(cosine_similarity > 0.8):
            # print(row_binary)
            # print(tmp)
            # print(cosine_similarity)
            empty_df.loc[len(empty_df)] = df2.iloc[index] # append row

    return (rename_columns(empty_df), list())


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
        "Requirements": ["Mitigations", 'Goals','Requirements'],
        "Mitigations": ["Requirements","Threats",'Mitigations','Attacks'],
        "Threats": ["Mitigations", "Attacks",'Threats'],
        "Goals": ['Requirements'],
        "Issues": ['Threats'],
        "Limitations": ['Threats'],
        "Vulnerabilities":['Attacks','Mitigations'],
        "Attacks":['Vulnerabilities','Threats']
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