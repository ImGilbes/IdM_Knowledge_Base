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

SECURITY_PROPERTIES = [
    "Authorization",
    "Authenticity",
    "Confidentiality",
    "Integrity",
    "Availability",
    "Non-repudiability"
]

PRIVACY_PROPERTIES = [
    "Confidentiality",
    "Unlinkability",
    "Anonymity and Pseudonymity",
    "Plausible Deniability",
    "Undetectability and Unobservability",
    "Awareness and Intervenability",
    "Compliance"
]

TRUST_PROPERTIES = [
    "Trust Establishment",
    "Trust Management"
]

USABILITY_PROPERTIES = [
    "User Interaction",
    "Accessibility"
]

HIGH_CATEGORIES = [
    "Laws and Regulations",
    "Infrastructure Management",
    "Trust",
    "Security",
    "Privacy",
    "Usability"
]

LOW_CATEGORIES = []

LOW_ENTITIES = [ "Requirements","Mitigations","Threats","Attacks","Vulnerabilities"]
HIGH_ENTITIES = [ "Goals","Issues","Limitations"]

def is_high_level_entity(name):
    if name in HIGH_CATEGORIES:
        return True
    return False

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
    tmp = []
    if "USER" in df.columns:
        tmp.append("USER")
    if "User" in df.columns:
        tmp.append("User")
    if "User-interaction" in df.columns:
        tmp.append("User-interaction")
    if "Adoption" in df.columns:
        tmp.append("Adoption")
    if "Generic" in df.columns:
        tmp.append("Generic")
    if "ServiceQuality" in df.columns:
        tmp.append("ServiceQuality")
    if "OP" in df.columns:
        tmp.append("OP")
    if "RP" in df.columns:
        tmp.append("RP")
    if "Functional" in df.columns:
        tmp.append("Functional")
    if "Abuse" in df.columns:
        tmp.append("Abuse")
    if "Technical" in df.columns:
        tmp.append("Technical")

    if "References" in df.columns:
        tmp.append("References")
    if "Description" in df.columns:
        tmp.append("Description")
    if "STRIDE" in df.columns:
        tmp.append("STRIDE")
    if "LINDDUN" in df.columns:
        tmp.append("LINDDUN")
    if "Ref" in df.columns:
        tmp.append("Ref")
    if "Impacts" in df.columns:
        tmp.append("Impacts")
    if "ORIGIN" in df.columns:
        tmp.append("ORIGIN")
    if "Abuse" in df.columns:
        tmp.append("Abuse")

    if "ORG IMPACT" in df.columns:
        tmp.append("ORG IMPACT")
    if "Organization" in df.columns:
        tmp.append("Organization")
    
    #this is just patchwork, waiting to have a better version of the tags
    df = df.drop(labels=tmp, axis=1)
    return df

    # match entity:
    #     case "Requirements":
    #         # return df.drop(labels=['References','Description'], axis=1)
    #         return df.drop(labels=['References','Description','OP','RP','Generic'], axis=1)
    #     case "Threats":
    #         # return df.drop(labels=['References','Description','Security','Privacy','STRIDE','LINDDUN'], axis=1)
    #         return df.drop(labels=['References','Description','Security','Privacy','STRIDE','LINDDUN','OP','RP','Generic'], axis=1)
    #     case "Mitigations":
    #         return df.drop(labels=['OP','RP','Generic'], axis=1).dropna(axis=1)
    #     case "Goals":
    #         # return df.drop(labels=['References','Description'], axis=1)
    #         return df.drop(labels=['References','Description','OP','RP'], axis=1)
    #     case "Issues":
    #         return df.drop(labels=["Description","Ref","Impacts","ORIGIN"], axis=1)
    #     case "Limitations":
    #         return df.drop(labels=["Description","Ref","Impacts","ORIGIN"], axis=1)
    #     case "Attacks":
    #         return df.drop(labels=["References"], axis=1)
    #     case "Vulnerabilities":
    #         return df.drop(labels=["Description","References"], axis=1)
    #     case _:
    #         return df

def index_cleanup(df):
    if "index" in df.columns:
        df.drop(labels=['index'],axis=1, inplace = True)
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


def build_high_level(df,entity_name):
    # assumption: we are working with a lower level entity
    #find trues

    if is_high_level_entity(entity_name):
        print("passed high level entity to build high level")
        return None

    new_df = pd.DataFrame(columns=HIGH_CATEGORIES)

    for index, _ in df.iterrows():

        security = "F"
        for property in SECURITY_PROPERTIES:
            if df[property][index] == "T":
                security = "T"
                break
        
        privacy = "F"
        for property in PRIVACY_PROPERTIES:
            if df[property][index] == "T":
                privacy = "T"
                break
        
        trust = "F"
        for property in TRUST_PROPERTIES:
            if df[property][index] == "T":
                trust = "T"
                break

        usability = "F"
        for property in USABILITY_PROPERTIES:
            if df[property][index] == "T":
                usability = "T"
                break
        
        law = "F"
        if entity_name == "Requirements":
            if df["Rights"][index] == "T":
                law = "T"
        elif entity_name == "Mitigations":
            if df["Rights"][index] == "T":
                law = "T"
                
        # TODO: add ORGANIZATION CATEGORIES here

        new_df.loc[index] = [law, "F", trust, security, privacy, usability]
    return new_df
    

def build_connections_table(name,definition,conn_entity):
    main_df = read_and_cleanup(name)
    df2 = read_and_cleanup(conn_entity).reset_index().drop(labels=["index"],axis=1)

    # find specific row in main df
    row = main_df[main_df[name] == definition].reset_index()
    row = index_cleanup(row)

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


    # need to convert to 0s and 1s because otherwise i cant do the cosine similarity

    if name == "Goals" and conn_entity == "Requirements":
        df_tmp = build_high_level(df2, conn_entity)
        df2_binary = df_tmp.replace({'T': 1, 'F': 0})
        row_binary = row.replace({'T': 1, 'F': 0}) # This is converted just fine
        row_binary.drop(labels=[name],axis=1, inplace=True)
    else:
        shared_cats = get_categories(main_df).intersection(get_categories(df2))
        # it should be sorted, but i should try
        row_binary = row[list(shared_cats)].replace({'T': 1, 'F': 0})
        df2_binary = df2[list(shared_cats)].replace({'T': 1, 'F': 0})

    empty_df = pd.DataFrame(columns=df2.columns)

    if is_high_level_entity(name):
        threshold = 0.80
    else:
        threshold = 0.60

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

        if(cosine_similarity > threshold):
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

# For how it is currently developed, this function creates a lot of duplicate results, which decrease the readability but also the performance - TO BE CHANGED in the future
@app.route('/generate_threats', methods=['POST'])
def generate_threats():
    # First version is direct from mitigations
    # Allow user to select some mitigations (check boxes on the right), then use a generate threats button
    # build_connections_table(name,definition,conn_entity)

    mitigations = request.json['Mitigations']
    requirements = request.json['Requirements']

    with open("./generated_threats.txt", "w"): # clear file before appending
        pass

# Get the mitigations connected to the selected requirements, then get the threats from the mitigations
    threats_set = set() # use a set to remove duplicates
    for el in requirements:
        mitigs_from_reqs, _ = build_connections_table("Requirements", el, "Mitigations")
        for el in mitigs_from_reqs["Mitigations"]:
            threats, _ = build_connections_table("Mitigations", el, "Threats")
            threats_set.update(threats["Threats"].to_list()) # this would remove duplicates in the file
            # file.write(threats["Threats"].to_csv(index=False))

# Write the threats deriving from mitigations
    for el in mitigations:
        threats, _ = build_connections_table("Mitigations", el, "Threats")
        threats_set.update(threats["Threats"].to_list())
        # file.write(threats["Threats"].to_csv(index=False))

    with open("./generated_threats.txt", "a") as file:
        for el in threats_set:
            file.write(f"{el}\n")

    return "ok"

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
    pd.set_option('future.no_silent_downcasting', True)
    app.run(debug=True)