The code which was used for data acquisition and plot generation may be found in this synced GitHub repository on OSF (confidential reviewer link: https://osf.io/zunmx/?view_only=5d4613b6cd374e2c8ab87dcb9cd68059). Additionaly, we provided the sqlite database with the raw data and the STATA code for statistical analysis. You may find these files in the OSF project. 
Please note that some files may not be displayed on OSF, but all files can be downloaded for closer examination of the code.


Below is short information on the main parts of the code. Detailed annotation may be found within the code as comment.
The order of code documents follows the structure in the supplemental document. Therefore, you just need to follow the code chronologically to follow along the data collection and data analysis process along. 

# S1_Data_collection
The 30 abstract used in this study were scraped from medrxiv using the paperscraper module. Please note that running this code will not create the same list of abstracts as used in our study, since the script (S1_Data_collection/S1_2_Collection_of_Abstracts.py) accesses the last 30 abstracts of the medrxiv dump. Depending on the date your dump was created this will result in a different list of papers. The list of abstracts we used in our study can be found here: (S1_Data_collection/S1_1_Collection_of_Abstracts_results.csv). Note that this list contains only metadata but no abstracts. 


# S2_Data_analyses
The figures for the map and the heatmap where created using this code.
In (S2_Data_analyses) is the file 'S2_2_a_individual_affiliation_effects_output.csv' located, which provides the association of individual affiliation and ChatGPTs recommendation for publication in the column for "aOR". The calculation of "aOR" is based on the raw data and was done in STATA.
'S2_Data_analyses/S2_2_b_Worldmap_get_geocode.ipynb' was used to get geocodes of the institutions. 'S2_Data_analyses/S2_2_b_Worldmap.ipynb' was used to create the worldmap figure in the main manuscript. 'S2_2_c_Heatmap.ipynb' was used to plot the heatmap in the main manuscript.
