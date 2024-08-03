import streamlit as st

def main():
    st.title("Welcome to the Financial Analysis App")
    st.write("""
    This application offers various financial tools and visualizations. Use the sidebar menu 
    or navigate through the pages using the menu at the top to explore different financial analyses:
    
    - **Interest Rate Sensitivity**: Explore how changes in the interest rate affect loan costs.
    - **Loan Calculator**: Calculate monthly payments on loans based on different interest rates and loan amounts.
    - **Other Tools**: Additional financial tools and data visualizations.

    Select a page above to get started.
    """)

if __name__ == "__main__":
    main()
