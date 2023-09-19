import streamlit as st
from publications import get_publication_data
from patents import get_patent_data
from make_dataframes import *
import pandas as pd
import json

token = st.secrets["token"]["value"]

def update_progress(value, progress_bar):
    progress_bar.progress(value)

def main():
    st.title("Search Form")
    
    # Input fields
    search_term_1 = st.text_input("Search Term 1:")
    search_term_2 = st.text_input("Search Term 2:")
    search_term_3 = st.text_input("Search Term 3:")
    search_term_4 = st.text_input("Search Term 4:")
    start_date = st.date_input("Start Date:")
    end_date = st.date_input("End Date:")
    patent_classification = st.text_input("Patent Classification:")
    operator = st.selectbox("Operator:", ["OR", "AND"])
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')


    progress_bar = st.progress(0)

    if st.button("Submit"):
        search_terms = [search_term_1, search_term_2, search_term_3, search_term_4]
        search_terms = [term for term in search_terms if term]
        patent_data = get_patent_data(start_date_str, end_date_str, search_terms, token, patent_classification, operator, progress_callback=lambda value: update_progress(value, progress_bar))
        publication_data = get_publication_data(start_date_str, end_date_str, search_terms, token) 
        
        # Process the data
        patents_found = len(patent_data)
        publications_found = publication_data['total']

        # Display results
        st.write(f"Patents found: {patents_found}")
        st.write(f"Publications found: {publications_found}")

        # Create and offer data for download
        ptable = patents_table(patent_data)
        atable = applicants_table(patent_data)
        ctable = cpc_classifications_table(patent_data)
        ctable = make_cpc(ctable, r"C:\Users\hvato01.KSAMK\Downloads\cpc_ultimate_titles.json")
        pubtable = publication_table(publication_data)
        authtable = extract_authors(publication_data)
        fstable = fields_of_study_table(publication_data)

        st.subheader("Patents Table")
        st.write(ptable)



        #st.download_button("Download Patents Excel", ptable.to_excel(index=False))
        #st.download_button("Download PatentApplicants Excel", atable.to_excel(index=False))
        #st.download_button("Download PatentClassifications Excel", ctable.to_excel(index=False))
        #st.download_button("Download Publications Excel", pubtable.to_excel(index=False))
        #st.download_button("Download PublicationAuthors Excel", authtable.to_excel(index=False))
        #st.download_button("Download PublicationFields Excel", fstable.to_excel(index=False))

if __name__ == "__main__":
    main()
