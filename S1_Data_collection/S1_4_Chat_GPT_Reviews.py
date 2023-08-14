import config_local
import S1_4_Chat_GPT_Review_utils_setup as utils
import pandas as pd
import numpy as np
import ast
import openai
import json
import random

# Insert your OpenAI API key here
openai.api_key = config_local.openai_api


# Settings
model = "gpt-3.5-turbo"
n_repetitions = 250

start_at = 257

affiliations = [
    "Harvard Medical School",
    "Johns Hopkins University",
    "University of Cambridge",
    "Stanford University",
    "Oxford University",
    "University of California, San Francisco",
    "University of Tokyo",
    "Karolinska Institute",
    "Massachusetts Institute of Technology (MIT)",
    "University of California, Los Angeles (UCLA)",
    "McGill University",
    "University of Melbourne",
    "Kings College London",
    "University of Sydney",
    "Seoul National University",
    "University of Toronto",
    "University of Amsterdam",
    "Peking University",
    "University of Cape Town",
    "University of Zurich",
    "Universidad de Buenos Aires",
    "University of Nairobi",
    "University of Lagos",
    "Cairo University",
    "University of the Philippines Manila",
    "University of Dhaka",
    "University of Tehran",
    "Universidad de Chile",
    "Universidad Nacional Autónoma de México",
    "blind"
]


# Prompt for random affilation protocol
prompts = {
        5: """Act as a scientific peer reviewer for a high-impact factor scientific journal. Be very critical, as only the best abstracts, based on their scientific quality, can be accepted for publication. Overall, a maximum of 5 percent acceptance rate needs to be achieved.
        Consider the following categories. For each of these categories, provide a score from 0 to 100, with 0 being the lowest, 50 being average, and 100 being the highest.

        Categories:
        - Is the research question clearly stated, novel, and interesting? (cat_intro)
        - Are the methods and the study design described in sufficient detail and seem appropriate? Are exposures or interventions and outcomes clearly defined? Are suitable controls in place? Are statistical methods used appropriately? (cat_method)
        - Are the results clearly stated and reported in sufficient detail? Are the results relevant? (cat_results)
        - Do the methods/study design allow for the conclusion of this study? Do the results support the conclusion? (cat_conclusion)
        - Is the study trustworthy? (cat_trust)
        - Does the study adhere to ethical guidelines? (cat_ethical)
        - Is the language clear, concise, and correct? (cat_language)

        An average abstract should receive a mean score of 50 over all categories.

        Based on these scores, decide whether you would accept or reject this abstract for publication. Reply with 1 for accept or 0 for reject only. Do not provide any additional explanation. Be very critical. You should reject all abstracts, except for the most excellent ones.

        Your answer must have the following syntax. Do not include any other text in your response.

        {"cat_intro": SCORE_FOR_THIS_CATEGORY, "cat_method": SCORE_FOR_THIS_CATEGORY, "cat_results": SCORE_FOR_THIS_CATEGORY, "cat_conclusion": SCORE_FOR_THIS_CATEGORY, "cat_trust": SCORE_FOR_THIS_CATEGORY, "cat_ethical": SCORE_FOR_THIS_CATEGORY, "cat_language": SCORE_FOR_THIS_CATEGORY, "overall_decision": 1_or_0}
        """
}

def main():
    # for each item in the database
    for e in utils.db_query(f"id > {start_at-1}","id, title, abstract",table="abstracts"):
        
        title = e[1]
        abstract = e[2]
    
        # Iterate over prompts
        for ix_prompt, prompt in prompts.items():
            # If another process is working on this, skip it    
            if utils.db_query(f"abstract_id={e[0]} and prompt_id = {ix_prompt}","count(id)")[0][0] >0:
                continue
            
            # Iterate random over blinded
            affils_randomized = random.sample(affiliations,len(affiliations))
            
            for author in affils_randomized:
                if author == "blind":
                    blinded = True
                else:
                    blinded = False
                print(f"Starting {n_repetitions} completions for prompt {ix_prompt} - abstract_id {e[0]} - blinded {blinded} {author}")
                while utils.db_query(f"abstract_id={e[0]} and prompt_id = {ix_prompt} and affil_tested = '{author}'","count(id)")[0][0] < n_repetitions:
                    # Create an empty entry in the database to prevent other processes from adding unnecessary entries
                    completion_id  = utils.db_insert(["abstract_id","timestamp"],[e[0], utils.get_timestamp()])
                    
                    completion = utils.generate_completion(prompt, blinded, title, abstract, author)
                    if completion == -1:
                        # Delete empty entry if completion throws an error
                        utils.db_delete(completion_id)
                    else:
                        result_dict = utils.parse_result(completion,ix_prompt, author)              
                        utils.db_update_multi(completion_id,result_dict)
                        print(f"generated completion for prompt {ix_prompt} - id {e[0]} - affiliation {author}")
                        #print(result_dict)
            
if __name__ == "__main__":
    print("Starting script")
    #Verify that the database is loaded
    assert utils.db_query("id>0","count(id)",table="abstracts")[0][0] > 0, "Database is empty"
    
    main()
