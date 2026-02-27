import streamlit as st
import pandas as pd
from io import BytesIO

def main():
    st.title("Excel Column Selector and Row Filter")
    st.write("Upload an Excel file, select columns, filter rows, and download the result.")

    # File upload
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])
    if uploaded_file:
        # Read the uploaded Excel file
        df = pd.read_excel(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df)

        # Column selection
        st.write("Select columns to include:")
        selected_columns = st.multiselect("Columns", df.columns.tolist(), default=df.columns.tolist())

        # Apply row filter: FTN column contains "7260R"
        if "FTN" in df.columns:
            filtered_df = df[df["FTN"].astype(str).str.contains("7260R", na=False)]
        else:
            st.error("The 'FTN' column is not found in the uploaded file.")
            return

        # Apply column selection
        filtered_df = filtered_df[selected_columns]

        # Display filtered table
        st.write("Filtered data:")
        st.dataframe(filtered_df)

        # Download filtered data
        st.write("Download filtered data:")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name="FilteredData")
        output.seek(0)
        st.download_button(
            label="Download Excel",
            data=output,
            file_name="filtered_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
