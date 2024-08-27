from flask import Flask, render_template, jsonify, request, redirect, url_for
import pandas as pd

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
    # if 'Name' in tmp:
    #     tmp.remove('Name')
    tmp.discard('Name')
    tmp.discard('Threats')
    tmp.discard('Requirements')
    tmp.discard('Mitigations')
    tmp.discard('Goals')
    
    return tmp

def cleanup_df(df,entity):
    # if index in set(df.columns):
    #     df = df.drop(labels=['index'], axis=1)
    if entity == "Requirements":
        return df.drop(labels=['References','Description','Addresses'], axis=1)
    elif entity == "Threats":
        return df.drop(labels=['References','Description','Security','Privacy','STRIDE','LINDDUN','Origin'], axis=1)
    elif entity == "Mitigations":
        return df.dropna(axis=1)


def simplify_table(df,entity):
    print(df)
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
    simplified_df = simplified_df.reset_index().set_index("index")
    return simplified_df


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_table', methods=['GET'])
def get_table():
    entity = request.args.get("entity")

    df = pd.read_csv(CSV_BASE_PATH + entity + ".csv")
    df = df.reset_index().set_index("index")
    df = cleanup_df(df,entity)

    df = simplify_table(df,entity)

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

def build_connections_table(name,definition):
    main_df = pd.read_csv(CSV_BASE_PATH + SPECIFIC_ENTITY + ".csv")
    # df = df.reset_index().set_index("index")
    # df = cleanup_df(df,SPECIFIC_ENTITY)
    if name == 'Requirements':
        name2 = "Mitigations"
        df2 = pd.read_csv(CSV_BASE_PATH + name2 + ".csv")
    elif name == 'Mitigations':
        name2 = "Requirements"
        df2 = pd.read_csv(CSV_BASE_PATH + name2 + ".csv")
    else:
        name2 = "Threats"
        df2 = pd.read_csv(CSV_BASE_PATH + name2 + ".csv")

    main_df = main_df.reset_index().set_index("index")
    main_df = cleanup_df(main_df,SPECIFIC_ENTITY)
    df2 = df2.reset_index().set_index("index")
    df2 = cleanup_df(df2,name2)

    # find specific row in main df
    row = main_df[main_df[name] == definition].reset_index()

    # interesect the categories between the two dfs
    selected_cats = set()
    # extract categories from the extracted row
    for cat in get_categories(main_df).intersection(get_categories(df2)):
        if row.at[0,cat] == 'T':
            selected_cats.add(cat)

    # select all rows in df2 that match the signature of the interesected categories
    mask = pd.Series([True] * len(df2))
    
    for col in selected_cats:
        mask &= df2[col].isin(['T'])


    return rename_columns(df2[mask])

@app.route('/get_specific', methods=['GET'])
def get_specific():
    global SPECIFIC_DEF
    global SPECIFIC_ENTITY
    if (SPECIFIC_DEF is not None) and (SPECIFIC_ENTITY is not None):

        starting_df = pd.read_csv(CSV_BASE_PATH + SPECIFIC_ENTITY + ".csv")
        starting_df[starting_df[SPECIFIC_ENTITY] == SPECIFIC_DEF].reset_index()

        df = build_connections_table(name=SPECIFIC_ENTITY,definition=SPECIFIC_DEF)
        # df = pd.read_csv(CSV_BASE_PATH + SPECIFIC_ENTITY + ".csv")
        
        # df = df.reset_index().set_index("index")
        # df = cleanup_df(df,SPECIFIC_ENTITY)
        # return jsonify(table_html=df.to_html(classes='data-table', index=False, index_names=False))
    else:
        df = pd.read_csv(CSV_BASE_PATH + "Requirements" + ".csv")
        df = df.reset_index().set_index("index")
        df = cleanup_df(df,"Requirements")


    return jsonify(starting_record=df.to_html(classes='data-table', index=False, index_names=False),
                   table_html=df.to_html(classes='data-table', index=False, index_names=False))
    

if __name__ == '__main__':
    app.run(debug=True)