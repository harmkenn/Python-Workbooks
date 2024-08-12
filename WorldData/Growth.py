import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

st.set_page_config(layout="wide",)

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('WorldData/Population Growth.csv')



# Create a Streamlit app
st.title('Population Growth Data')

# Add a dropdown menu with all the country names
df = df.dropna()

# ML to predict Growth Rate

# Split data into features (X) and target (y)
X = df.iloc[:, [2, 4, 5, 6, 7, 8]]
gr = df.iloc[:, [3]]

# Set regression model parameters
params = {
    "n_estimators": 500,
    "max_depth": 4,
    "min_samples_split": 5,
    "learning_rate": 0.01,
    "loss": "squared_error",  # Least squares loss (you can adjust this)
}

# Initialize the Gradient Boosting Regressor
reg_gr = GradientBoostingRegressor(**params)

# Fit the model to the training data
reg_gr.fit(X, gr)


countries = df['Country Name'].unique()

country = st.sidebar.selectbox('Select a Country', countries)

# Filter the data based on the selected country
filtered_df = df[df['Country Name'] == country]
#st.write(filtered_df)

# Add number input for each column
columns = filtered_df.columns

# Create a dictionary to store the number inputs
number_inputs = {}

# Loop through each column and create a number input
for column in columns:
    if column not in ['Country Code', 'Country Name']:
        # Set the step based on the data type of the column
        if filtered_df[column].dtype == 'int64':
            format = "%d"  # Format for integers
            step = 1
        elif filtered_df[column].dtype == 'float64':
            format = "%.6f"  # Show 6 decimal places
            step = 0.001
        else:
            format = "%.3f"  # Show 3 decimal places
            step = 1

        value = st.sidebar.number_input(f'{column}',
                                        value=filtered_df.iloc[0][column],
                                        step=step,
                                        format=format)
        number_inputs[column] = value

# Create a range of years from 2023 to 2073
years = np.arange(2023, 2074)

# Create a list to store the future population values
future_population = []

start_pop = number_inputs['Population2023']
growth_rate = number_inputs['GrowthRate2023']

# Loop through each year and calculate the future population
for year in years:
    # Calculate the future population using the formula: Current Population x (1 + Growth Rate)^Number of Years
    future_pop = start_pop * np.exp(growth_rate * (year - 2023))

    # Append the year and the corresponding future population to the list as a dictionary
    future_population.append({'year': year, 'pop': future_pop})

# Create a Plotly scatterplot
fig = px.scatter(future_population, x='year', y='pop')

# Update the layout
fig.update_layout(title='Future Population Projection (2023-2073)',
                  xaxis_title='Year',
                  yaxis_title='Population')

# Display the plot
st.plotly_chart(fig)

st.write(df)
