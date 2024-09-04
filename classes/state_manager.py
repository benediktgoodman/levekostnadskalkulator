from pydantic import BaseModel, Field, validate_call
from typing import Optional, Union
import pandas as pd
import numpy as np

from pathlib import Path
import sys


# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from functions.calc_funcs import calculate_amortization_schedule  # noqa: E402

class ScenarioState(BaseModel):
    """
    A class used to represent the state of the scenario builder page.

    ...

    Attributes
    ----------
    df : Optional[pd.DataFrame]
        a pandas DataFrame containing data related to the scenario
    selected_house_price : Optional[Union[float, int, np.floating, np.integer]]
        the price of the selected house
    selected_interest_rate : Optional[Union[float, int, np.floating, np.integer]]
        the interest rate for the loan
    total_loan : Union[float, int, np.floating, np.integer]
        the total amount of the loan
    monthly_payment : Union[float, int, np.floating, np.integer]
        the monthly payment for the loan
    total_interest : Union[float, int, np.floating, np.integer]
        the total interest paid over the life of the loan
    loan_to_value : Union[float, int, np.floating, np.integer]
        the loan-to-value ratio
    total_cost_a : Union[float, int, np.floating, np.integer]
        the total cost for scenario A
    total_cost_b : Union[float, int, np.floating, np.integer]
        the total cost for scenario B
    loan_amount : Union[float, int, np.floating, np.integer]
        the total amount of the loan
    ownership_fraq : Union[float, int, np.floating, np.integer]
        the ownership fraction
    loan_amount_a : Union[float, int, np.floating, np.integer]
        the amount of the loan for scenario A
    loan_amount_b : Union[float, int, np.floating, np.integer]
        the amount of the loan for scenario B
    schedule_a : Optional[pd.DataFrame]
        the amortization schedule for scenario A
    schedule_b : Optional[pd.DataFrame]
        the amortization schedule for scenario B
    calculation_done : bool
        a flag indicating whether the calculations have been done

    Methods
    -------
    update(filtered_df, selected_house_price, ek, ammortisation_periods)
        Updates the state of the scenario based on new data
    """
    class Config:
        arbitrary_types_allowed = True
    
    df: Optional[pd.DataFrame] = None
    selected_house_price: Optional[Union[float, int, np.floating, np.integer]] = Field(None, ge=0)
    selected_interest_rate: Optional[Union[float, int, np.floating, np.integer]] = Field(None, ge=0, le=1)
    total_loan: Union[float, int, np.floating, np.integer] = Field(0, ge=0)
    monthly_payment: Union[float, int, np.floating, np.integer] = Field(0, ge=0)
    total_interest: Union[float, int, np.floating, np.integer] = Field(0, ge=0)
    loan_to_value: Union[float, int, np.floating, np.integer] = Field(0, ge=0, le=100)
    total_cost_a: Union[float, int, np.floating, np.integer] = Field(0, ge=0)
    total_cost_b: Union[float, int, np.floating, np.integer] = Field(0, ge=0)
    loan_amount: Union[float, int, np.floating, np.integer] = Field(0, ge=0)
    ownership_fraq: Union[float, int, np.floating, np.integer] = Field(0, ge=0, le=1)
    loan_amount_a: Union[float, int, np.floating, np.integer] = Field(0, ge=0)
    loan_amount_b: Union[float, int, np.floating, np.integer] = Field(0, ge=0)
    schedule_a: Optional[pd.DataFrame] = None
    schedule_b: Optional[pd.DataFrame] = None
    calculation_done: bool = False



    @validate_call(config=dict(arbitrary_types_allowed = True))
    def update(self, filtered_df: pd.DataFrame, selected_house_price: float, ek: float, ammortisation_periods: int):
        """
        Updates the state of the scenario based on new data.

        Parameters
        ----------
        filtered_df : pd.DataFrame
            a pandas DataFrame containing data related to the scenario
        selected_house_price : float
            the price of the selected house
        ek : float
            the down payment for the loan
        ammortisation_periods : int
            the number of periods over which the loan will be amortized
        """
        
        if not self.selected_interest_rate:
            raise ValueError("Interest rate must be provided to update the scenario")
        

        self.total_loan = selected_house_price - ek
        self.monthly_payment = filtered_df["monthly_loan_payment"].iloc[0]
        self.total_interest = self.monthly_payment * ammortisation_periods - self.total_loan
        self.loan_to_value = (self.total_loan / selected_house_price) * 100
        self.total_cost_a = filtered_df["a_total"].iloc[0]
        self.total_cost_b = filtered_df["b_total"].iloc[0]
        self.loan_amount = selected_house_price - ek
        self.ownership_fraq = filtered_df["ownership_fraq"].iloc[0]
        self.loan_amount_a = self.loan_amount * self.ownership_fraq
        self.loan_amount_b = self.loan_amount * (1 - self.ownership_fraq)
    
        # Assume calculate_amortization_schedule is imported or defined elsewhere
        self.schedule_a = calculate_amortization_schedule(
            self.loan_amount_a, self.selected_interest_rate, ammortisation_periods
        )
        self.schedule_b = calculate_amortization_schedule(
            self.loan_amount_b, self.selected_interest_rate, ammortisation_periods
        )
        self.calculation_done = True
