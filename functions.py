#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 17:58:32 2024

@author: Sodik Umurzakov
"""

# =============================================================================
# This file inludes several functions used for calculattion of Taylor Rule Rate and 
# plot several plot for final results
# =============================================================================

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def taylor_rule_rate(inflation_rate, output_gap, r_star, pi_star, alpha1, alpha2):
    """
    Function to calculate the Taylor Rule Rate, a theoretical interest rate suggested
    by the Taylor Rule for monetary policy decisions.

    Parameters:
    - inflation_rate: Observed inflation rate (%).
    - output_gap: Output gap, i.e., the percentage difference between 
      actual output and potential output.
    - r_star: Targeting interest rate (%), representing the neutral rate.
    - pi_star: Target inflation rate (%), in practice it is seted by central banks.
    - alpha1: Weight on inflation deviation from the target.
    - alpha2: Weight on the output gap.

    Returns:
    - taylor_rate_rule: The Taylor Rule rate calculated as:
        r_star + inflation_rate + alpha1 * (inflation_rate - pi_star) + alpha2 * output_gap
    """
    
    # Calculate the Taylor Rule interest rate
    taylor_rate_rule = (
        r_star 
        + inflation_rate 
        + alpha1 * (inflation_rate - pi_star)  # Contribution from inflation gap
        + alpha2 * output_gap                  # Contribution from output gap
    )
    
    return taylor_rate_rule  # Return the computed Taylor Rule rate


def taylor_rule_rate_with_unemp(inflation_rate, output_gap, unemployment_rate, r_star, pi_star, alpha1, alpha2, alpha3, u_n):
    """
    Function to calculate the Taylor Rule Rate with an added unemployment gap component.

    Parameters:
    - inflation_rate: Observed inflation rate (%).
    - output_gap: Output gap, i.e., the percentage difference between actual output and potential output.
    - unemployment_rate: Observed unemployment rate (%).
    - r_star: Neutral interest rate (%), representing the natural rate of interest.
    - pi_star: Target inflation rate (%), typically set by central banks.
    - alpha1: Weight on the inflation deviation from the target.
    - alpha2: Weight on the output gap.
    - alpha3: Weight on the unemployment gap.
    - u_n: Natural unemployment rate (%), representing the unemployment rate at full employment.

    Returns:
    - taylor_rate_rule: The Taylor Rule rate calculated as:
        r_star + inflation_rate + alpha1 * (inflation_rate - pi_star) + alpha2 * output_gap - alpha3 * (unemployment_rate - u_n)
    """
    
    # Calculate the Taylor Rule interest rate with unemployment gap
    taylor_rate_rule = (
        r_star 
        + inflation_rate 
        + alpha1 * (inflation_rate - pi_star)   # Contribution from inflation gap
        + alpha2 * output_gap                   # Contribution from output gap
        - alpha3 * (unemployment_rate - u_n)    # Contribution from unemployment gap
    )
    
    return taylor_rate_rule  # Return the computed Taylor Rule rate






def plot_taylor_rule_vs_mro(
    df, 
    title="Taylor Rule vs. Actual MRO Rate", 
    ylabel="Interest Rate (%)", 
    xlabel="Year",
    highlight_periods=None,
    annotate_points=None
):
    """
    Function to plot Taylor Rule vs. Actual MRO Rate with professional styling.

    Parameters:
    - df: DataFrame containing "Year", "Taylor Rule Rate", and "MRO Rate".
    - title: Title of the plot.
    - ylabel: Label for the y-axis.
    - xlabel: Label for the x-axis.
    - highlight_periods: List of periods to highlight [(start_year, end_year, label, color)].
    - annotate_points: List of points to annotate [(year, rate, label)].

    Returns:
    - None
    """

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot the Taylor Rule Rate
    ax.plot(
        df["Year"], 
        df["Taylor Rule Rate"], 
        label="Taylor Rule Rate", 
        color="blue", 
        linewidth=2.5,
        linestyle="--"
    )
    
    # Plot the Taylor Rule Rate with Unemp
    ax.plot(
        df["Year"], 
        df["Taylor Rule Rate (Unemployment)"], 
        label="Taylor Rule Rate (Unemployment)", 
        color="red", 
        linewidth=2.5,
        linestyle="--"
    )

    # Plot the Actual MRO Rate
    ax.plot(
        df["Year"], 
        df["MRO Rate"], 
        label="Actual MRO Rate", 
        color="orange", 
        linewidth=2.5,
        linestyle="-"
    )

    # Highlight periods
    if highlight_periods:
        for start, end, label, color in highlight_periods:
            ax.axvspan(start, end, color=color, alpha=0.2, label=label)

    # Set the title and labels
    ax.set_title(title, fontsize=16, weight="bold", loc="center")
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)

    # Customize the grid
    ax.grid(which="major", linestyle="--", linewidth=0.7, alpha=0.7)
    ax.grid(which="minor", linestyle=":", linewidth=0.5, alpha=0.5)

    # Customize the x-axis
    ax.set_xticks(df["Year"])  # Set ticks to include all years
    ax.set_xticklabels(df["Year"], rotation=45, fontsize=10)  # Rotate and set font size

    # Annotate points
    if annotate_points:
        for year, rate, label in annotate_points:
            ax.annotate(
                label,
                xy=(year, rate),
                xytext=(year + 1, rate + 1),  # Adjust annotation position
                arrowprops=dict(facecolor="black", arrowstyle="->"),
                fontsize=12,
                color="darkred"
            )

    # Add a legend
    ax.legend(
        loc="upper left",
        fontsize=12,
        frameon=True,
        framealpha=0.9,
        shadow=True,
        edgecolor="gray"
    )

    # Adjust the layout to prevent clipping
    plt.tight_layout()


