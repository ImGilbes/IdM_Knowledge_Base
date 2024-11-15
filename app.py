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

THREAT_TO_LOW_CATEGORIES_MAP = {"Spoofing":"Authenticity", 
              "Tampering":"Integrity", 
              "Repudiation": "Non-repudiability",
              "Information Disclosure": "Confidentiality",
              "Denial of Service": "Availability",
              "Elevation of Priviledge": "Authorization",
              "Linking":"Unlinkability",
              "Identification": "Anonymity and Pseudonymity",
              "Non-repudiation": "Plausible Deniability",
              "Detecting": "Undetectability and Unobservability",
              "Unawareness and Unintervenability": "Awareness and Intervenability",
              "Non-compliance": "Compliance",
              "Access denial": "Accessibility",
              "Unusable system": "Usability",
              "Lack of Trust" : "Trust Management",
              "Lack of Trust" : "Trust Establishment",
              "Digital Infrastructure Management":"Digital Infrastructure Management",
              "Actors and Assets Management": "Actors and Assets Management"
              }

LOW_TO_THREAT_CATEGORIES_MAP = dict(zip(THREAT_TO_LOW_CATEGORIES_MAP.values(), THREAT_TO_LOW_CATEGORIES_MAP.keys()))


SECURITY_PROPERTIES = [
    "Authorization",
    "Authenticity",
    "Confidentiality",
    "Integrity",
    "Availability",
    "Non-repudiability"
]

STRIDE_PROPERTIES = [
    "Spoofing",
    "Tampering",
    "Repudiation",
    "Information Disclosure",
    "Denial of Service",
    "Elevation of Priviledge"
]

LINDDUN_PROPERTIES = [
    "Linking",
    "Identification",
    "Non-repudiation",
    "Detecting",
    "Unawareness and Unintervenability",
    "Non-compliance"
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

USABILITY_THREAT_PROPERTIES = [
    "Unusable system",
    "Access denial"
]

ORGANIZATIONAL_PROPERTIES = [
    "Digital Infrastructure Management",
    "Actors and Assets Management"
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

THREAT_CATEGORIES = [
    "Digital Infrastructure Management",
    "Actors and Assets Management",
    "Rights",
    "Spoofing",
    "Tampering",
    "Repudiation",
    "Information Disclosure",
    "Denial of Service",
    "Elevation of Priviledge",
    "Linking",
    "Identification",
    "Non-repudiation",
    "Detecting",
    "Unawareness and Unintervenability",
    "Non-compliance",
    "Lack of Trust",
    "Unusable system",
    "Access denial"
]

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

    if "References" in df.columns:
        tmp.append("References")
    if "Description" in df.columns:
        tmp.append("Description")
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
    return df.drop(labels=tmp, axis=1)

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

    if is_high_level_entity(entity_name):
        print("passed high level entity to build high level")
        return None

    string_or = lambda a, b: "F" if a == "F" and b == "F" else "T" 

    new_df = pd.DataFrame(columns=[entity_name]+HIGH_CATEGORIES)

    new_df[entity_name] = df[entity_name] 
    security = df["Authenticity"] if entity_name != "Threats" else df["Spoofing"]
    privacy = df["Unlinkability"] if entity_name != "Threats" else df["Linking"]
    usability = df["Accessibility"] if entity_name != "Threats" else df["Access denial"]
    trust = df["Trust Establishment"] if entity_name != "Threats" else df["Lack of Trust"]
    org = df["Digital Infrastructure Management"] if entity_name != "Threats" else df["Digital Infrastructure Management"]
    
    property_list = SECURITY_PROPERTIES if entity_name != "Threats" else STRIDE_PROPERTIES
    for property in property_list:
        security = security.combine(df[property], func = string_or)
    new_df["Security"] = security

    property_list = PRIVACY_PROPERTIES if entity_name != "Threats" else LINDDUN_PROPERTIES
    for property in property_list:
        privacy = privacy.combine(df[property], func = string_or)
    new_df["Privacy"] = privacy

    property_list = USABILITY_PROPERTIES if entity_name != "Threats" else USABILITY_THREAT_PROPERTIES
    for property in property_list:
        usability = usability.combine(df[property], func = string_or)
    new_df["Usability"] = usability

    if entity_name in ["Requirements", "Mitigations"]:
        for property in TRUST_PROPERTIES:
            trust = trust.combine(df[property], func = string_or)
    
        for property in ORGANIZATIONAL_PROPERTIES:
            org = org.combine(df[property], func = string_or)

    new_df["Trust"] = trust
    new_df["Infrastructure Management"] = org

    match entity_name:
        case "Requirements":
            new_df["Laws and Regulations"] = df["Rights"]
        case "Mitigations":
            new_df["Laws and Regulations"] = df["Rights"]
        case "Threats":
            new_df["Laws and Regulations"] = df["Rights"]
            print(new_df)

    return new_df


# Convert mitigation categories to threat
def build_low_level_to_threat(df,entity_name):

    if is_high_level_entity(entity_name):
        print("passed high level entity to build high level")
        return None

    string_or = lambda a, b: "F" if a == "F" and b == "F" else "T" 

    trust = df["Trust Establishment"].combine(df["Trust Management"], func = string_or)
    df["Trust Establishment"] = trust
    df.drop(labels=["Trust Management"], axis=1, inplace=True)

    org = df["Digital Infrastructure Management"].combine(df["Actors and Assets Management"], func = string_or)
    df["Digital Infrastructure Management"] = org
    df.drop(labels=["Actors and Assets Management"], axis=1, inplace=True)

    return df

def build_connections_table(name,definition,conn_entity):
    main_df = read_and_cleanup(name)
    df2 = read_and_cleanup(conn_entity).reset_index().drop(labels=["index"],axis=1)
    conn_entity_original = df2.copy(deep=True)
    empty_df = pd.DataFrame(columns=df2.columns)

    definition = definition.strip() # this is here to avoid weird problems in the future

    threshold = 0.8 if is_high_level_entity(name) else 0.60 # threashold for the similarity metric to select a record

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

    match name:
        case "Goals":
            if conn_entity == "Requirements" :
                df2 = build_high_level(df2, "Requirements")

        case "Requirements":
            if conn_entity in ["Mitigations","Requirements"] :
                pass

            elif conn_entity == "Goals":
                main_df = build_high_level(main_df, "Requirements")

        case "Mitigations":
            if conn_entity in ["Mitigations","Requirements"]:
                pass
            elif conn_entity in ["Threats", "Attacks", "Vulnerabilities"]:
                # convert mitigations to threats
                main_df = build_low_level_to_threat(main_df, "Mitigations")
                main_df.rename(columns=LOW_TO_THREAT_CATEGORIES_MAP, inplace=True)

        case "Threats":
            if conn_entity in ["Mitigations"]:
                df2 = build_low_level_to_threat(df2, "Mitigations")
                df2.rename(columns=LOW_TO_THREAT_CATEGORIES_MAP, inplace=True)

            elif conn_entity in ["Attacks","Vulnerbilities"]:
                pass

        case "Issues":
            if conn_entity in ["Threats"]:
                df2 = build_high_level(df2, "Threats")

        case "Limitations":
            if conn_entity in ["Threats"]:
                df2 = build_high_level(df2, "Threats")

        case _:
            return None
    
    # find specific row in main df
    row = main_df[main_df[name] == definition].reset_index()
    row = index_cleanup(row)

    shared_cats = get_categories(main_df).intersection(get_categories(df2))
    row_binary = row[list(shared_cats)].replace({'T': 1, 'F': 0})
    df2_binary = df2[list(shared_cats)].replace({'T': 1, 'F': 0})

    print("\n\n SELECTED ROW\n")
    print(row_binary)
    print("\n\n SELECTED connection\n")
    print(df2_binary)
    print("\n\n SELECTED connection columns\n")
    print(df2_binary.columns)
    print("\n\n ROW  columns\n")
    print(row_binary.columns)
    print(f"\n\n are the columns the samelength? {len(df2_binary.columns)} vs {len(row_binary.columns)} \nare the columns the same, and in the same order??? {df2_binary.columns == row_binary.columns }\n")

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
            empty_df.loc[len(empty_df)] = conn_entity_original.iloc[index] # append row

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
    with open("./generated_mitigations.txt", "w"): # clear file before appending
        pass

# Get the mitigations connected to the selected requirements, then get the threats from the mitigations
    threats_set = set() # use a set to remove duplicates
    mitigations_set = set()
    for el in requirements:
        mitigs_from_reqs, _ = build_connections_table("Requirements", el, "Mitigations")
        mitigations_set.update(mitigs_from_reqs["Mitigations"].to_list())
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
    with open("./generated_mitigations.txt", "a") as file:
        for el in mitigations_set:
            file.write(f"{el}\n")

    print("Finished threats output")

    return "ok"

@app.route('/get_specific', methods=['GET'])
def get_specific():
    global SPECIFIC_DEF
    global SPECIFIC_ENTITY

    starting_record = None

    # connections = {
    #     "Requirements": ["Mitigations", 'Goals','Requirements'],
    #     "Mitigations": ["Requirements","Threats",'Mitigations','Attacks'],
    #     "Threats": ["Mitigations", "Attacks",'Threats'],
    #     "Goals": ['Requirements'],
    #     "Issues": ['Threats'],
    #     "Limitations": ['Threats'],
    #     "Vulnerabilities":['Attacks','Mitigations'],
    #     "Attacks":['Vulnerabilities','Threats']
    # }
    connections = {
        "Requirements": ["Mitigations", 'Goals','Requirements'],
        "Mitigations": ["Requirements","Threats",'Mitigations'],
        "Threats": ["Mitigations", 'Threats'],
        "Goals": ['Requirements'],
        "Issues": ['Threats'],
        "Limitations": ['Threats']
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