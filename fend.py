import streamlit as st
import pandas as pd
import json
import reconsile

def load_json(file):
    data = json.loads(file.read())
    return data

def show_tables():
    with open('reconciliation_metadata.json', 'r') as f:
        metadata = json.load(f)
    st.write(metadata)
    for company in metadata['CompaniesIdentifier']:
        with open(company+".json", 'r') as f:
            table = json.load(f)
        st.write(company + " : ")
        table = pd.json_normalize(table)
        st.write(table)

def main():
    st.title("Reconciliation demo")
    st.subheader("Flow after data extraction")

    st.write("List of companies customer is dealing with")
    show_tables()

    uploaded_file = st.file_uploader("Enter extracted data here",type='json')
    if uploaded_file is not None:
        # st.write(uploaded_file)
        json_data = load_json(uploaded_file)
        with open('temp.json', 'w') as f:
            json.dump(json_data, f)
        # df = pd.json_normalize(json_data)
        st.write(json_data)
        reconsile.pipe_line('temp.json')

if __name__ == "__main__":
    main()