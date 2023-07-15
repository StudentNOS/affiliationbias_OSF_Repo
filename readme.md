Here is short information on the main parts of the code. Detailed annotation may be found within the code as comment. 

# Medrxiv scraping
The 30 abstract used in this study were scraped from medrxiv using the paperscraper module. Please note that running this code will not create the same list of abstracts as used in our study, since [the script](medrxiv_scraping/get_abstracts.py) accesses the last 30 abstracts of the medrxiv dump. Depending on the date your dump was created this will result in a different list of papers. The list of abstracts we used in our study can be found [here](medrxiv_scraping/medrxiv_last30_noabstracts.csv). Note that this list contains only metadata but no abstracts. 

# Data collection
Start with data collection and follow instructions given in the code as comments


# Map_Plot 
The figures for the map and the heatmap where created using this code.
In 'analysed_data' is the file 'Aff_individual_output_with_true_mean_as_base.csv' located, which provides the association of individual affiliation and ChatGPTs recommendation for publication in the column for "aOR". The calculation of "aOR" is based on the raw data (see further description below) and was done in STATA. This file is used for the heatmap and worldmap in the main manuscript. 
The file affiliation_with_geocode gets created using the "Get_geocode.ipynb" and is the basis for the Worldmap that gets plotted in "World_map_plot.ipynb".
"heatmap.ipynb" contains the code for the heatmap plot. 


# Raw data 
The raw data (all runs and responses from GPT) will be provided in the OSF repository after publication. During review the raw data will be provided if requested. 
