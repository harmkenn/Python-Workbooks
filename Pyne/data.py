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

        # Row filtering
        st.write("Filter rows based on conditions:")
        filters = {}
        for col in selected_columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                min_val, max_val = st.slider(f"Filter {col} (numeric)", float(df[col].min()), float(df[col].max()), (float(df[col].min()), float(df[col].max())))
                filters[col] = (min_val, max_val)
            elif pd.api.types.is_string_dtype(df[col]):
                unique_values = df[col].unique()
                selected_values = st.multiselect(f"Filter {col} (categorical)", unique_values, default=unique_values)
                filters[col] = selected_values

        # Apply filters
        filtered_df = df[selected_columns]
        for col, condition in filters.items():
            if isinstance(condition, tuple):  # Numeric filter
                filtered_df = filtered_df[(filtered_df[col] >= condition[0]) & (filtered_df[col] <= condition[1])]
            else:  # Categorical filter
                filtered_df = filtered_df[filtered_df[col].isin(condition)]

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
