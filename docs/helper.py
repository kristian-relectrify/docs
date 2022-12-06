import pandas as pd
import numpy as np 

import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import seaborn as sns

import statsmodels.api as sm

def process_degradation_model(data):
    average_ = data.groupby('x').mean()
    std_ = data.groupby('x').std()
    
    return average_, std_

def process_revolve_model(mdl, std, init_soh):
    average_init = 100*(mdl[mdl.y <= init_soh]/init_soh)
    std_init = 100*(std[average_init.index.min()-1:]/init_soh)

    average_init.reset_index(drop=True,inplace=True)
    std_init.reset_index(drop=True,inplace=True)
    
    return average_init, std_init

def plot_degradation_model(mdl, std):
    
    ## get linear fit
    X = mdl.index.values.reshape((-1,1))
    Y = mdl.y.values.reshape((-1,1))
    X = sm.add_constant(X)
    
    model = sm.OLS(Y,X)
    linear_fit = model.fit()
    
    y_pred = linear_fit.predict()
    R2_adj = round(linear_fit.rsquared_adj,2)
    deg_per_100 = round(linear_fit.params[1] * 100 * -1,2)
    
    fig, ax = plt.subplots(figsize=(20,10))
    
    ax.plot(mdl.index, Y, 
            ls='-', c='#5fff67',
            marker='o', ms=0.2)
    
    ax.plot(mdl.index, y_pred, ls='--', lw=2, c='white')

    ax.fill_between(x=mdl.index, 
                    y1=mdl.y - 2*std.y, 
                    y2= mdl.y + 2*std.y, 
                    alpha=0.2, 
                    color='#5fff67',
                    label= '2 std. dev')

    ax.set_xlabel("Number of Cycles", size=24, color='white', labelpad=20, loc='left')
    ax.set_ylabel("SOH [%]", size=24, color='white', labelpad=20, loc='center')

    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.grid(axis='both', which='major', alpha=0.5)
    ax.grid(axis='both', which='minor', alpha=0.2)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(22)
        tick.label.set_color('white')

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(22) 
        tick.label.set_color('white')

    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')

    msg = 'Degradation per 100 cycles = {}%\nAjd. R2 = {}'.format(deg_per_100, R2_adj)
    ax.text(x=0, y=40, s=msg, va='bottom', ha='left', color='white', size=22, rotation=0)
    
    ax.set_title("Observed battery degradation", size=30, loc='left', color='white', pad=40)
    ax.set_facecolor("black")
    fig.set_facecolor("black")
    
    return None

def plot_revolve_model(mdl, std, eol_pct, init_cap_kwh):
    eol_index = mdl[mdl <= eol_pct].dropna().index.min()

    fig, ax = plt.subplots(figsize=(20,10))

    ax.plot(mdl.index, mdl.y, 
            ls='-', c='#5fff67',
            marker='o', ms=0.2)

    ax.fill_between(x=mdl.index, 
                    y1=mdl.y - 2*std.y, 
                    y2= mdl.y + 2*std.y, 
                    alpha=0.2, 
                    color='#5fff67',
                    label= '2 std. dev')

    ax.axvline(x=2000, c='white', ls='--')
    ax.axvline(x=eol_index, c='red', ls='--')
    ax.axhline(y=65, c='red', ls='--')

    ax.set_xlabel("Number of Cycles", size=24, color='white', labelpad=20, loc='left')
    ax.set_ylabel("Pack SOH [%]", size=24, color='white', labelpad=20, loc='center')

    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.grid(axis='both', which='major', alpha=0.5)
    ax.grid(axis='both', which='minor', alpha=0.2)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(22)
        tick.label.set_color('white')

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(22) 
        tick.label.set_color('white')

    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')

    msg = '2000th Cycle Mark\nE[SOH] = {}% (+/- {}%)\nEnergy capacity = {} kWh'.format(
        round(mdl.iloc[2000][0], 2), 
        round(std.iloc[2000][0] * 2,0),
        round(init_cap_kwh*mdl.iloc[2000][0]/100,2))
    ax.text(x = 1980, y = 100, s=msg, 
            color='white', size=22, ha='right', va='top')

    msg = '~{} cycles (EoL)'.format(round(eol_index, -2))
    ax.text(x=eol_index, y=100, s=msg, va='top', ha='right', color='white', size=22, rotation=90)

    msg = 'End of life (EoL) or\n{}% from initial capacity'.format(eol_pct)
    ax.text(x=0, y=eol_pct+1, s=msg, va='bottom', ha='left', color='white', size=28)

    ax.set_title("ReVolve Expected Cycle Life with Initial\nPack SOH of 60%", size=30, loc='left', color='white', pad=40)
    ax.set_facecolor("black")
    fig.set_facecolor("black")