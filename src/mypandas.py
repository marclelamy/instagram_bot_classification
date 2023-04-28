def foo (): 
    print('oui')


import labelling as l
import pandas as pd
import plotly.express as px



class Mypandas(pd.DataFrame):
    def better_value_count(self, column, round=3, dropna=True): 
        '''Returns a Dataframe with value count and value count
        normalized for a specific column.
        
        Parameter 
        ---------
        column, str: columns to get the value count from
        '''
        
        val_count = self[column].value_counts()
        val_count_normalized = self[column].value_counts(normalize=True).round(round)
        
        if dropna == False:
            val_count_na = self[column].value_counts(dropna=False)
            val_count_na_normalized = self[column].value_counts(dropna=False, normalize=True).round(round)

            df_val_count = pd.concat([val_count, val_count_normalized, val_count_na, val_count_na_normalized], axis=1)
            df_val_count.columns = ['wo_na', 'wo_na_norm', 'w_na', 'w_na_norm']

        else: 
            df_val_count = pd.concat([val_count, val_count_normalized], axis=1)
            df_val_count.columns = ['wo_na', 'wo_na_norm']

        return df_val_count.sort_values('wo_na_norm', ascending=False)



    def column_user_distribution (self, column_to_analyse, rmv_values=[], rmv_labelled_values=True):
        # Load and split data
        df_labels = load_labels(include_all=True)
        bots = df_labels.query('label == 1')['username'].tolist()
        otherbots = df_labels.query('label == 3')['username'].tolist()
        legits = df_labels.query('label == 0')['username'].tolist()
        df_main = self.query(f'{column_to_analyse} not in @rmv_values').reset_index(drop=True)

        df_main[column_to_analyse] = df_main[column_to_analyse].astype('category')
        df_bots = df_main.query("username in @bots")
        df_otherbots = df_main.query("username in @otherbots")
        df_legits = df_main.query("username in @legits")

        # Counting how many times each categories has been used 
        df_col = df_main[column_to_analyse].value_counts().to_frame().reset_index()
        df_col.columns = [column_to_analyse, "count"]

        for index, sub_df in enumerate([df_main, df_bots, df_legits, df_otherbots]):
            # Looking at how many distinct users used the categories and how many time the coment has been collected
            for num in [0, 3, 1]:
                sub_df = sub_df[["username", column_to_analyse]]
                column_name = ["user_count", "bot_count", "legit_count", 'otherbot_count'][index]

                # Removing duplicates and changing col name
                if num == 1: 
                    sub_df = sub_df.drop_duplicates()
                    column_name = column_name + "_unique" # for "no duplicate"


                # group by categories, get the count of username for each
                # comment_count = sub_df.groupby(column_to_analyse)\
                #                                 .count()\
                #                                 .reset_index()\
                #                                 .to_numpy()
                comment_count = sub_df[column_to_analyse].value_counts().reset_index().to_numpy()

                comment_count_dict = {i:j for i, j in comment_count}


                # Counting by how many users each categoriess has been used for
                df_col[column_name] = df_col[column_to_analyse].apply(lambda x: comment_count_dict[x] if x in comment_count_dict.keys() else 0)


        # Removing values that have been 100% labelled
        if rmv_labelled_values == True:
            df_col = df_col.query("count > bot_count + legit_count + otherbot_count")


        return df_col.sort_values(by="count", ascending=False).reset_index(drop=True)



    def split_df_by_label(self): 
        '''Subset a df info multiple each having one label. 
        It returns n dfs, n being number of labels'''
        return [self.query(f'label == {label}') for label in sorted(self.label.unique())]


    def describe_column_by_label(self, column): 
        '''Describes a given column for each label'''
        all_dfs = self.split_df_by_label()
        df_describe = pd.concat(all_dfs, axis=1).astype(int)
        df_describe.columns = [0, 1, 2, 3]
        
        df_plolty = df_describe.stack().to_frame().reset_index()
        df_plolty.columns = ['Statistic', 'Label', 'value']
        fig = px.histogram(df_plolty,
                           x='Statistic',
                           y='value',
                           color='Label',
                           barmode='group',
                           title=f"Summary stats per label for column {column.replace('_', ' ')}"
                           ).update_layout(yaxis_title=column.replace('_', ' ').title())

        return df_describe, fig