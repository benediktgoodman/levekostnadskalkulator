# Boligkostnadskalkulatoren (Housing Cost Calculator)

## Overview

Boligkostnadskalkulatoren is a comprehensive web application designed to help users calculate and visualize the true costs of homeownership in Norway. This tool provides insights into various aspects of housing expenses, including mortgage payments, electricity costs, and other fixed expenses.

## Features

- **Loan Cost Calculator**: Visualize how interest rates affect monthly mortgage payments.
- **Electricity Cost Calculator**: Estimate monthly electricity costs based on usage and prices, including Norway's electricity subsidy scheme.
- **Custom Scenario Builder**: Create and analyze personalized housing cost scenarios.
- **Interactive Visualizations**: Explore data through intuitive charts and graphs.
- **Cost Breakdown Analysis**: Understand the distribution of housing-related expenses.
- **Amortization Schedule**: View how loan balance and interest payments change over time.
- **Data Export**: Download calculated data for further analysis.

## Technology Stack

- Python 3.11
- Streamlit
- Pandas
- NumPy
- Plotly

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Boligkostnadskalkulatoren.git
   cd Boligkostnadskalkulatoren
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

## Usage

To run the Streamlit app:

```
streamlit run 00_🏠_Hjem.py
```

Navigate through the different pages to access various calculators and analyses:

- 🏠 Home: Overview of the application
- 💰 Loan Cost Calculator
- ⚡ Electricity Cost Calculator
- 🏗️ Custom Scenario Builder

## Configuration

Adjust the `variables.toml` file to modify default values and ranges for various inputs used throughout the application.

## Contributing

Contributions to improve Boligkostnadskalkulatoren are welcome. Please feel free to submit pull requests or open issues to discuss proposed changes or report bugs.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Author

Benedikt Goodman <goodmanbenedikt@gmail.com>

## Acknowledgements

Special thanks to the developers of Python, Pandas, Numpy, Plotly and Streamlit