# -*- coding: utf-8 -*-
"""
Created on Sun May 21 19:00:25 2023

@author: bened
"""

import numpy as np
import pandas as pd
"""
Antar: 
Årlig bruk på 13800 kwh (relativt høyt estimat)
Spotpris lik siste 13 måneders gjennomsnitt: 224,73
Månedlig strømregning (inkl mva + strømstøtte) = 1150

Kalkulator:
https://slipper.no/stromstotte-kalkulator/

"""
# Set elprice
avg_elpris = 300

# support func
def make_fixed_cost(*args):
    """sums arbitrary stuff"""
    return sum(args)

def loan_calc(loan, rate, months):
    """Gir månedlige beløp for en gitt lånesum med en gitt rente over 30 år"""
    return (rate/12) * (1/(1-(1+rate/12)**(-months)))*loan

#%%

elpris = 350

def monthly_price_calculator(houseprice, 
                             rate, 
                             fixed_cost_house, 
                             elprice,
                             b_fk = 12349,
                             p_fk = 12000,
                             transaction_costs = 200000,
                             ek = 2280000,
                             b_fraq = 0.33):
    
    
    # trekk fra omkostninger ved boligkjøp
    eff_ek = ek - transaction_costs
    
    # Lokale konstanter for lånsbalanse 
    loan = houseprice - eff_ek
    
    if loan > 5925000:
        msg = ['Maksimalt lånebeløp oversteget.',
               'Maks lån tillatt er 5925000.',
               f'Beregnet lån med input er {loan}']
        return(print(' '.join(msg)))
    
    # Antar eierfraksjon basert på excel data
    p_fraq = 1 - b_fraq
    
    # Få månedlige lånekostnader
    monthly_loan = pd.Series(loan_calc(loan, rate, 360))
    
    # Sammenstill dataframe
    df = pd.DataFrame(monthly_loan, columns=['lån_total']).assign(
        rente = rate,
        elpris = elpris
        )
    
    # Regn ut totalbeløp på lån + elpris og felleskosnader
    df['fk_hus'] = fixed_cost_house
    df['total_beløp'] = df['lån_total'] + df['elpris'] + df['fk_hus']
    df['b_beløp_hus'] = (df['lån_total'] * b_fraq) + (df['elpris']/2) + (df['fk_hus']/2)
    df['p_beløp_hus'] = (df['lån_total'] * p_fraq) +  (df['elpris']/2)  + (df['fk_hus']/2)
    
    # Legg til faste månedlige kostnader
    df['b_total'] = df['b_beløp_hus'] + b_fk
    df['p_total'] = df['p_beløp_hus'] + p_fk
    
    return df


#%%

eff_rente = np.arange(3.0, 8.0, 0.25) / 100

df_hovin_renter = pd.concat([
    monthly_price_calculator(
        7100000, 
        rente, 
        4000, 
        500, 
        transaction_costs=200000, 
        b_fraq=0.4,
        ek=1900000) 
        for rente in eff_rente]
    ).reset_index(drop=True)


#%%

pris_vektor = np.arange(6500000, 7700000, 50000)

df_prisendring = (
    pd.concat(
        [monthly_price_calculator(
            price, 
            0.06, 
            4000, 
            500, 
            transaction_costs=200000,
            ek = 1950000,
            b_fraq=0.33) 
            for price in pris_vektor]
        )
    .reset_index(drop=True)
    .assign(pris=pris_vektor)
    )