import S1_4_Chat_GPT_Review_utils_setup as utils
import pandas as pd
import json

# Define path to save file
save_path = "export/data_random_affil.csv"

# Get completion count from database
completions = utils.db_query("id>0","COUNT(ID), COUNT(DISTINCT abstract_id)") # Check if data is plausible.
print(f"Found {completions[0][0]} completions for {completions[0][1]} abstracts")

res = utils.db_query("id>0 and prompt_id=5","id as completion_id, abstract_id, prompt_id, affil_tested, gpt_accept, category_scores, meta")    

df_completions = pd.DataFrame(res,columns=["completion_id","abstract_id","prompt_id","affil_tested","gpt_accept","category_scores","meta"])


# Normalize category scores
for i, e in df_completions.iterrows():
    if not e.category_scores or e.category_scores.startswith("99"):
        continue
    else:
        #print(e.category_scores, type(e.category_scores), e.category_scores == 999)
        for key in json.loads(e.category_scores).keys():
            df_completions.loc[i,key] = json.loads(e.category_scores)[key]


df_abstracts = pd.DataFrame(utils.db_query("id>0","id, title, abstract, date, author_list, doi",table="abstracts"), columns=["id", "title", "abstract", "date", "author_list", "doi"])

print(f"Found {df_abstracts.shape[0]} abstracts")

# Export to file
df_export = pd.merge(df_completions, df_abstracts, left_on="abstract_id", right_on="id", how="left")
# Drop unnecessary columns
df_export.drop(["id","meta","author_list"],axis=1,inplace=True)
df_export.sort_values(by="abstract_id",ascending=True,inplace=True)

df_export.to_csv(save_path,sep=";",index=False)
print("Exported to", save_path)

