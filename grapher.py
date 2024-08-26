import pandas as pd


data_path = "./data/"


goals = pd.read_csv(data_path + "Goals.csv")
reqs = pd.read_csv(data_path + "Requirements.csv")
threats = pd.read_csv(data_path + "Threats.csv")
mitigs = pd.read_csv(data_path + "Mitigations.csv")


print(mitigs)

# rslt_df = dataframe[dataframe['Percentage'] > 70]
print(mitigs[mitigs['Socio-political']=='T' ])
print(mitigs[mitigs['Socio-political']=='T'])


