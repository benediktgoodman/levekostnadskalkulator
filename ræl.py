import pandas as pd
import numpy as np
from functions.calc_functions import monthly_price_calculator

interest_rates = np.arange(3.0, 8.0, 0.25) / 100
price_vectors = np.arange(6500000, 7700000, 50000)


df_hovin_renter = pd.concat([
    monthly_price_calculator(
        7100000, 
        rente, 
        4000, 
        500, 
        transaction_costs=200000, 
        ownership_fraq=0.4,
        ek=1900000) 
        for rente in interest_rates]
    ).reset_index(drop=True)



df_prisendring = (
    pd.concat(
        [monthly_price_calculator(
            price, 
            0.06, 
            4000, 
            500, 
            transaction_costs=200000,
            ek = 1950000,
            ownership_fraq=0.33) 
            for price in price_vectors]
        )
    .reset_index(drop=True)
    .assign(pris=price_vectors)
    )