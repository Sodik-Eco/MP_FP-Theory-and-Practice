#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 16:26:12 2024

@author: Sodik Umurzakov
"""
# =============================================================================
# PROBLEM 1: Taylor Rule vs MRO Rate
# =============================================================================



# =============================================================================
#Pre-run: If you need to install packages, please, intall necessary packages, then perform before running code:
#!pip install pandas, numpy, matplotlib
# The code can be implemented with python version python =/> 3.7.16 
# =============================================================================

# Import necessary libraries and modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from functions import taylor_rule_rate, taylor_rule_rate_with_unemp, plot_taylor_rule_vs_mro

# =============================================================================
# Give path to the data in GitHub
url = "https://raw.githubusercontent.com/Sodik-Eco/MP_FP-Theory-and-Practice/main/raw_data"

# List of datasets to load
file_names = [
    "ameco_data_new.xlsx",
    "ecb_mro_data_new.xlsx", # Data from 2000 to 2008
    "ecb_mro_data.csv"  # To use data from 2009 to 2024
]

# Dictionary to store loaded data
datasets = {}

# Loop through file names and upload each file
for file_name in file_names:
    file_url = f"{url}/{file_name}"  # Construct the raw URL
    if file_name.endswith(".xlsx"):
        datasets[file_name] = pd.read_excel(file_url, engine="openpyxl")
    elif file_name.endswith(".csv"):
        datasets[file_name] = pd.read_csv(file_url, delimiter=",")
    else:
        print(f"Unsupported file format for {file_name}")



# Upload AMECO and ECB MRO data
ameco_data = datasets["ameco_data_new.xlsx"]
# Data from 2000 to 2008
ecb_data_new = datasets["ecb_mro_data_new.xlsx"]
# Data from 2009 to 2024
ecb_data = datasets["ecb_mro_data.csv"]
# =============================================================================



# =============================================================================
# Data Cleaning and Transformation
# Data transformatin
ecb_data_new["DATE"] = pd.to_datetime(ecb_data_new["DATE"])
ecb_data_new["Year"] = ecb_data_new["DATE"].dt.year
# Just take arithmatic mean of MRO from daily data to average
ecb_data["DATE"] = pd.to_datetime(ecb_data["DATE"])
ecb_data["Year"] = ecb_data["DATE"].dt.year

# Filter the dataframes
ecb_data_new_filtered = ecb_data_new[ecb_data_new["Year"].between(2000, 2008)]
ecb_data_filtered = ecb_data[ecb_data["Year"].between(2009, 2024)].rename(columns={
    "Main refinancing operations - fixed rate tenders (fixed rate) (date of changes) - Level (FM.D.U2.EUR.4F.KR.MRR_FR.LEV)": "OBS.VALUE"
})


# Just take arithmatic mean of MRO from daily data to average
ecb_data_final = ecb_data_filtered.groupby("Year")['OBS.VALUE'].mean()
ecb_data_new_final = ecb_data_new_filtered.groupby("Year")['OBS.VALUE'].mean()

# Concatenate the filtered dataframes
mro_annual = pd.concat([ecb_data_new_final, ecb_data_final])

# Define variables to filter and their corresponding new column names
variables = {
    "CPI, Harmonised (ZCPIH)": "HICP",
    "GDP, at constant prices (OVGD)": "GDP",
    "Potential GDP (OVGDP)": "Potential_GDP",
    "GDP, price deflator (PVGD)": "GDP_deflator",
    "Unemployment, Total (NUTN)": "Total_Unemployment",
    "Total labour force (NLTN)": "Total_Labour_Force",
    "Gap between actual GDP and trend GDP, percentage of trend GDP (AVGDGT)": "Output_Gap_trend_GDP"
}

# Create an empty DataFrame to store filtered results
filtered_data = pd.DataFrame()

# Define the range of years
year_range = list(range(1999, 2025))

# Create an empty DataFrame with years as the index
ameco_filtered_data = pd.DataFrame(index=year_range)

# Loop through each variable, filter the data and add it as a new column
for variable, column_name in variables.items():
    # Filter rows for the specific variable
    filtered_rows = ameco_data[ameco_data["Variable"] == variable]

    # Extract year columns, handle "-" as 0, transpose, and add to the DataFrame
    if not filtered_rows.empty:
        data_series = (
            filtered_rows.iloc[0, 7:]  # Extract year columns starting from 1999
            .replace("-", 0)          # Replace "-" with 0
            .astype(float)            # Convert to float
            .fillna(0)                # Fill NaN with 0
        )
        data_series.name = column_name
        ameco_filtered_data[column_name] = data_series


# Calculate inflation rate (annualized percentage change in HICP)
ameco_filtered_data["Inflation_rate"] = (ameco_filtered_data["HICP"].pct_change() * 100).fillna(0)

# Calculate output gap and replcae inf to 0
ameco_filtered_data["Output_gap"] = (((ameco_filtered_data["GDP"] - ameco_filtered_data["Potential_GDP"]) / ameco_filtered_data["Potential_GDP"]) * 100).replace([np.inf, -np.inf], 0).astype(float)

# =============================================================================


# PROMLEM 1.1

# Taylor Rule Rate without unemp by calling function taylor_rule_rate
Taylor_rule_rate_original = taylor_rule_rate(ameco_filtered_data["Inflation_rate"], 
                                             ameco_filtered_data["Output_gap"], 
                                             r_star = 2, # Equilibrium real interest rate
                                             pi_star = 2, # Inflation target
                                             alpha1 = 0.5, 
                                             alpha2 = 0.5).drop(index=1999) # Now we drop 1999

# Use TR to compare with MRO
# Construct comparison df
comparison_years = mro_annual.index
comparison_df = pd.DataFrame({
    "Year": comparison_years,
    "Taylor Rule Rate": Taylor_rule_rate_original.values,
    "MRO Rate": mro_annual.values
})
# comparison_df.to_excel('Taylor_Rule_vs_MRO_Rate_new26.xlsx', index=False)


# Plot Taylor Rule Rate againts MRO Rate
# Define highlight periods
highlight_periods = [
    (2007, 2009, "Global Financial Crisis", "green"),  # Global Financial Crisis
    (2020, 2021, "COVID-19 Pandemic", "gray"),         # COVID-19
    (2022, 2024, "Russo-Ukrainian Conflict", "red") # Russo-Ukrainian conflict
]

# Define annotation points
annotate_points = [
    (2012, comparison_df.loc[comparison_df["Year"] == 2012, "MRO Rate"].values[0], "Policy Deviation"),
    (2020, comparison_df.loc[comparison_df["Year"] == 2020, "MRO Rate"].values[0], "COVID-19 Impact")
]

# Call the function
plot_taylor_rule_vs_mro(
    comparison_df, 
    title="Taylor Rule vs. Actual MRO Rate (Euro Area)", 
    ylabel="Interest Rate (%)", 
    xlabel="Year",
    highlight_periods=highlight_periods,
    annotate_points=annotate_points
)


# Save the plot before showing it
# os.makedirs("results", exist_ok=True)
output_path = os.path.join("results", "taylor_rule_vs_mro.png")
plt.savefig(output_path, dpi=300, bbox_inches="tight")
# Display the plot
plt.show()





# =============================================================================
# PROBLEM 1.4: Does larger output weight (α2 = 1) fundamentally alter the Taylor rule’s
# assessment of the evolution of the monetary policy stance?

# Taylor Rule Rate without unemp by calling function taylor_rule_rate
Taylor_rule_rate_original_alph_1 = taylor_rule_rate(ameco_filtered_data["Inflation_rate"], 
                                             ameco_filtered_data["Output_gap"], 
                                             r_star = 2, # Equilibrium real interest rate
                                             pi_star = 2, # Inflation target
                                             alpha1 = 0.5, 
                                             alpha2 = 1).drop(index=1999) # Now we drop 1999


# Construct comparison df
comparison_years_alpha_1 = mro_annual.index
comparison_df_alpha_1 = pd.DataFrame({
    "Year": comparison_years_alpha_1,
    "Taylor Rule Rate": Taylor_rule_rate_original_alph_1.values,
    "MRO Rate": mro_annual.values
})
# comparison_df.to_excel('Taylor_Rule_vs_MRO_Rate_new26.xlsx', index=False)


# Plot Taylor Rule Rate againts MRO Rate
# Call the function
plot_taylor_rule_vs_mro(
    comparison_df_alpha_1, 
    title="Taylor Rule vs. Actual MRO Rate (Euro Area)", 
    ylabel="Interest Rate (%)", 
    xlabel="Year",
    highlight_periods=highlight_periods,
    annotate_points=annotate_points
)


# Save the plot before showing it
# os.makedirs("results", exist_ok=True)
output_path = os.path.join("results", "taylor_rule_vs_mro_alpha_1.png")
plt.savefig(output_path, dpi=300, bbox_inches="tight")
# Display the plot
plt.show()

# =============================================================================



# =============================================================================
# PROBLEM 1.5
# In the AMECO data base you will find a couple of data series for the output
# gap and the inflation rate which were also mentioned in class. Plot your
# rule projections for another price deflator (CPI, GDP deflator), and another
# version of the output gap for the Euro Area. How far do results change? (2p)

ameco_filtered_data["GDP_deflator_pc"] = (ameco_filtered_data["GDP_deflator"].pct_change() * 100).fillna(0)


Taylor_rule_rate_original_def = taylor_rule_rate(ameco_filtered_data["GDP_deflator_pc"], 
                                             ameco_filtered_data["Output_Gap_trend_GDP"], 
                                             r_star = 2, # Equilibrium real interest rate
                                             pi_star = 2, # Inflation target
                                             alpha1 = 0.5, 
                                             alpha2 = 0.5).drop(index=1999) # Now we drop 1999


# Construct comparison df
comparison_years = mro_annual.index
comparison_df = pd.DataFrame({
    "Year": comparison_years,
    "Taylor Rule Rate": Taylor_rule_rate_original_def.values,
    "MRO Rate": mro_annual.values
})
# comparison_df.to_excel('Taylor_Rule_vs_MRO_Rate_new26.xlsx', index=False)


# Plot Taylor Rule Rate againts MRO Rate
# Call the function
plot_taylor_rule_vs_mro(
    comparison_df, 
    title="Taylor Rule vs. Actual MRO Rate (Euro Area)", 
    ylabel="Interest Rate (%)", 
    xlabel="Year",
    highlight_periods=highlight_periods,
    annotate_points=annotate_points
)


# Save the plot before showing it
# os.makedirs("results", exist_ok=True)
output_path = os.path.join("results", "taylor_rule_vs_mro_deflator.png")
plt.savefig(output_path, dpi=300, bbox_inches="tight")
# Display the plot
plt.show()
# =============================================================================



# =============================================================================
# PROBLEM 1.6
# Add unemployment to the Taylor rule. Plot your rule projection against the
# actual interest rate and the Taylor rule projection. Did the rule projection
# improve? (1p)

ameco_filtered_data["Unemployment_rate"] = (ameco_filtered_data["Total_Unemployment"]/ameco_filtered_data["Total_Labour_Force"])*100

Taylor_rule_rate_with_unemployment = taylor_rule_rate_with_unemp(ameco_filtered_data["Inflation_rate"], 
                                             ameco_filtered_data["Output_gap"], 
                                             ameco_filtered_data["Unemployment_rate"],
                                             r_star = 2, # Equilibrium real interest rate
                                             pi_star = 2, # Inflation target
                                             alpha1 = 0.5, 
                                             alpha2 = 0.5,
                                             alpha3 = 0.5,
                                             u_n = 6).drop(index=1999) # Now we drop 1999

# Construct comparison df
comparison_years_unemp = mro_annual.index
comparison_df_unemp = pd.DataFrame({
    "Year": comparison_years_unemp,
    "Taylor Rule Rate": Taylor_rule_rate_original.values,
    "Taylor Rule Rate (Unemployment)": Taylor_rule_rate_with_unemployment.values,
    "MRO Rate": mro_annual.values
})
# comparison_df.to_excel('Taylor_Rule_vs_MRO_Rate_new26.xlsx', index=False)


# Plot Taylor Rule Rate againts MRO Rate
# Call the function
plot_taylor_rule_vs_mro(
    comparison_df_unemp, 
    title="Taylor Rule vs. Actual MRO Rate (Euro Area)", 
    ylabel="Interest Rate (%)", 
    xlabel="Year",
    highlight_periods=highlight_periods,
    annotate_points=annotate_points
)


# Save the plot before showing it
# os.makedirs("results", exist_ok=True)
output_path = os.path.join("results", "taylor_rule_vs_mro_unemp.png")
plt.savefig(output_path, dpi=300, bbox_inches="tight")
# Display the plot
plt.show()
# =============================================================================



