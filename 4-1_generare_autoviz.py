import src.labelling as sl
import sqlite3
import pandas as pd 
import numpy as np
from autoviz.AutoViz_Class import AutoViz_Class




df_main = sl.load_main()
df_labels = sl.load_labels()
 
df_main = df_main.merge(df_labels, how='left', on='username')

# either fillna, either dropna, depending on the use case, comment/uncomment
# df_main['label'] = df_main['label'].fillna(2).astype(int)
df_main = df_main.dropna(subset='label').reset_index(drop=True)

# df_main = sl.Mypandas(df_main)
df_main.head()



AV = AutoViz_Class()

# Generate the visualizations


df_autoviz = df_main.copy(deep=True)
df_autoviz['label'] = df_autoviz['label'].apply(lambda x: 1 if x == 3 else x)

for column in df_autoviz:
    if any([x in column for x in ['min', 'max', 'avg', 'sum', 'concat']]): 
        df_autoviz = df_autoviz.drop(column, axis=1)
        continue

    print(column)


dftc = AV.AutoViz(filename='', 
                  sep ='' , 
                  depVar ='follow_count', 
                  dfte = df_autoviz, 
                  header = 0, 
                  verbose = 1,  # print extra information on the notebook and also display charts
                  lowess = True, 
                  chart_format ='server', 
                  max_rows_analyzed = df_autoviz.shape[0], 
                  max_cols_analyzed = df_autoviz.shape[1],
                  )