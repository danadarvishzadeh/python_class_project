from sklearn import tree
import mysql.connector
from sklearn.preprocessing import OneHotEncoder
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import LabelEncoder



cnx = mysql.connector.connect(user='dana', password='32343234aaa', database='buy_list')
cursor = cnx.cursor()

query = "SELECT * FROM bama"

cursor.execute(query)

pre_df = []
for model, usage, city, year, price in cursor:
    pre_df.append([model, usage, city, year, price])


cursor.close()
cnx.close()

df = pd.DataFrame(pre_df, columns = ['model', 'usage', 'city', 'year', 'price'])  
le = LabelEncoder()
df.model = le.fit_transform(df.model)
df.city = le.fit_transform(df.city)
X = df[['model', 'usage', 'city', 'year']].values
Y = df.price

clf = tree.DecisionTreeClassifier()
clf.fit(X, Y)

requested_data = input('please insert in model,usage,city,year format:\n')
requested_data = requested_data.strip().split(',')
requested_data = list(map(lambda x : x.strip(), requested_data))
requested_data = pd.DataFrame([requested_data], columns = ['model', 'usage', 'city', 'year'])
requested_data.model = le.fit_transform(requested_data.model)
requested_data.city = le.fit_transform(requested_data.city)

answer = clf.predict(requested_data)

print('predicted price is:\n', answer)