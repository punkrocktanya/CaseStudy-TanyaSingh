"""Publication-sized charts from saved results; no model retraining."""

# Make shared task modules importable when running this file directly.
import sys as _task_sys
from pathlib import Path as _TaskPath
_task_scripts = _TaskPath(__file__).resolve().parents[1]
for _task_dir in ("task1_data_engineering", "task2_degradation_modeling", "task3_anomaly_detection", "task4_rul_estimation", "task5_pack_scaling", "task6_reporting"):
    _task_path = str(_task_scripts / _task_dir)
    if _task_path not in _task_sys.path:
        _task_sys.path.append(_task_path)

from pathlib import Path
import sys
import json
import ast
import hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.preprocessing import RobustScaler
from stage_04_fit_capacity_fade import predict
sys.path.append(str(Path(__file__).resolve().parents[2] / '.local_deps'))

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'scripts/task6_reporting/outputs/14_reporting_visualization'
OUT.mkdir(parents=True, exist_ok=True)
CELLS = ['001_2','002_4']
plt.rcParams.update({'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False,
                     'axes.titleweight':'bold', 'savefig.facecolor':'white'})
SOURCES = ['scripts/task2_degradation_modeling/outputs/04_capacity_fade/cycle_capacity_analysis.csv',
           'scripts/task2_degradation_modeling/outputs/04_capacity_fade/model_parameters.csv', 'scripts/task2_degradation_modeling/outputs/04_capacity_fade/predictions.csv',
           'scripts/task3_anomaly_detection/outputs/07_anomaly_detection/anomaly_features.csv',
           'scripts/task4_rul_estimation/outputs/10_rul_lstm/predictions.csv','scripts/task4_rul_estimation/outputs/09_rul_xgboost/predictions.csv',
           'scripts/task4_rul_estimation/outputs/11_rul_model_comparison/all_attempts.csv']


def read(path):
    return pd.read_csv(ROOT/path,dtype={'Dataset_ID':str})


def save(fig, name):
    fig.savefig(OUT/f'{name}.png',dpi=220,bbox_inches='tight')
    fig.savefig(OUT/f'{name}.pdf',bbox_inches='tight')
    plt.close(fig)


def stop_at_zero(x, y):
    """Display only: terminate at interpolated first zero; retain original arrays."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    hits = np.flatnonzero(y <= 0)
    if not len(hits):
        return x.copy(), y.copy(), None
    j = int(hits[0])
    if j == 0:
        return np.array([]), np.array([]), None
    crossing = x[j-1] + (x[j]-x[j-1]) * y[j-1] / (y[j-1]-y[j])
    return np.r_[x[:j], crossing], np.r_[y[:j], 0.], float(crossing)


def main():
    data,params,forecasts,anomaly,lstm,xgb,rul_all = [read(s) for s in SOURCES]
    fig,axes=plt.subplots(1,2,figsize=(12,4.5),constrained_layout=True)
    palette={'Linear':'#4477AA','Exponential':'#EE7733','Square-root time':'#228833','Power law':'#AA3377'}
    for ax,cell in zip(axes,CELLS):
        g=data[data.Dataset_ID==cell].sort_values('Cycle_Index')
        reference=float(g.loc[g.Cycle_Index==2,'Discharge_Capacity_Ah'].iloc[0])
        threshold=0.8*reference
        eol=int(g.loc[g.Discharge_Capacity_Ah<threshold,'Cycle_Index'].iloc[0])
        shown=g[g.Cycle_Index<=eol]
        ax.scatter(shown.Cycle_Index,shown.Discharge_Capacity_Ah,s=20,color='black',label='Measured',zorder=5)
        for row in params[(params.Dataset_ID==cell)&(params.Scope=='full_series')].itertuples():
            values=predict(row.Model,ast.literal_eval(row.Parameters),shown.n.to_numpy(),shown.t_days.to_numpy())
            # Do not display model values after they fall below the EOL threshold.
            keep=np.flatnonzero(values < threshold)
            end=int(keep[0]) if len(keep) else len(values)
            ax.plot(shown.Cycle_Index.iloc[:end],values[:end],color=palette[row.Model],label=row.Model)
        ax.axhline(threshold,color='#CC3311',linestyle='--',label='80% of cycle 2')
        ax.axvline(eol,color='grey',linestyle=':',label=f'Observed EOL: cycle {eol}')
        ax.scatter([eol],[g.loc[g.Cycle_Index==eol,'Discharge_Capacity_Ah'].iloc[0]],color='#CC3311',s=36,zorder=6)
        ax.set(title=f'{cell}: capacity to observed EOL',xlabel='Cycle index',ylabel='Discharge capacity (Ah)')
        ax.legend(fontsize=8); ax.grid(alpha=.2)
    save(fig,'01_capacity_predictive_curves')

    fig,axes=plt.subplots(1,2,figsize=(12,4.5),constrained_layout=True)
    ce_summary=[]
    for ax,cell in zip(axes,CELLS):
        g=data[data.Dataset_ID==cell].sort_values('Cycle_Index')
        flags=g[g.Coulombic_Efficiency_pct>100]
        ax.plot(g.Cycle_Index,g.Coulombic_Efficiency_pct,color='#4477AA',marker='.',label='Integrated diagnostic CE')
        ax.axhline(100,color='grey',linestyle='--',label='100% review threshold')
        ax.scatter(flags.Cycle_Index,flags.Coulombic_Efficiency_pct,color='#CC3311',marker='D',zorder=5,label='CE > 100%')
        for r in flags.itertuples():
            ax.annotate(str(r.Cycle_Index),(r.Cycle_Index,r.Coulombic_Efficiency_pct),xytext=(3,7),textcoords='offset points',fontsize=8)
        ax.set(title=f'{cell}: {len(flags)} flagged cycles',xlabel='Cycle index',ylabel='Coulombic efficiency (%)')
        ax.margins(y=.2);ax.grid(alpha=.2);ax.legend(fontsize=8,loc='lower left')
        ce_summary.append(dict(Dataset_ID=cell,Flagged_Cycles=', '.join(map(str,flags.Cycle_Index)),Median_CE_Pct=g.Coulombic_Efficiency_pct.median()))
    save(fig,'02_coulombic_efficiency')
    pd.DataFrame(ce_summary).to_csv(OUT/'ce_summary.csv',index=False)

    fig,axes=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
    features=['Residual_Detrended_Ah','Change_Deviation_Pct','CE_Deviation']
    for j,cell in enumerate(CELLS):
        g=anomaly[anomaly.Dataset_ID==cell].copy()
        valid=g.dropna(subset=features+['DBSCAN_Label']).copy()
        z=RobustScaler().fit_transform(valid[features])
        valid['Scaled_Residual']=z[:,0];valid['Scaled_Change']=z[:,1]
        ax=axes[0,j]
        for label in sorted(valid.DBSCAN_Label.unique()):
            m=valid.DBSCAN_Label==label
            noise=label==-1
            ax.scatter(valid.loc[m,'Scaled_Residual'],valid.loc[m,'Scaled_Change'],
                       marker='x' if noise else 'o',s=40 if noise else 25,
                       color='#CC3311' if noise else None,alpha=.8,
                       label='Noise (-1)' if noise else f'Cluster {int(label)}')
        count=int((valid.DBSCAN_Label==-1).sum())
        ax.set(title=f'{cell}: {count}/{len(valid)} noise points',xlabel='Detrended capacity residual (scaled)',ylabel='Capacity-change deviation (scaled)')
        ax.legend(fontsize=8);ax.grid(alpha=.2)
        ax=axes[1,j]
        ax.plot(g.Cycle_Index,g.Discharge_Capacity_Ah,color='grey',linewidth=1,label='Measured')
        flagged=g[g.DBSCAN_Label==-1]
        ax.scatter(flagged.Cycle_Index,flagged.Discharge_Capacity_Ah,color='#CC3311',marker='x',label='DBSCAN noise')
        ax.set(title=f'{cell}: flagged cycles on capacity trajectory',xlabel='Cycle index',ylabel='Discharge capacity (Ah)')
        ax.legend(fontsize=8);ax.grid(alpha=.2)
    save(fig,'03_deviation_clusters')

    selected=lstm[(lstm.Window==3)&(lstm.Checkpoint==8)]
    selected.to_csv(OUT/'rul_distribution_samples_checkpoint8.csv',index=False)
    fig,axes=plt.subplots(1,2,figsize=(12,4.5),constrained_layout=True)
    distribution=[]
    for ax,cell in zip(axes,CELLS):
        g=selected[selected.Dataset_ID==cell]
        values=g.Predicted_RUL.dropna().to_numpy()
        actual=int(g.Actual_RUL.iloc[0])
        xv=int(xgb[(xgb.Dataset_ID==cell)&(xgb.Checkpoint_Cycle==8)].Predicted_RUL_Cycles.iloc[0])
        low=int(min(values.min(),actual,xv))-2;high=int(max(values.max(),actual,xv))+2
        bins=np.arange(low-.5,high+1.5)
        ax.hist(values,bins=bins,color='#4477AA',alpha=.7,edgecolor='white',label='LSTM seed counts (n=3)')
        ax.axvline(actual,color='black',linestyle='--',linewidth=2,label=f'Actual RUL = {actual}')
        ax.axvline(xv,color='#EE7733',linestyle=':',linewidth=2,label=f'XGBoost RUL = {xv}')
        ax.set(title=f'{cell}: forecast from cycle 8',xlabel='Forecasted remaining cycles',ylabel='Number of LSTM runs',yticks=[0,1,2,3],xticks=np.arange(low,high+1))
        ax.grid(axis='y',alpha=.2);ax.legend(fontsize=8)
        distribution.append(dict(Dataset_ID=cell,Checkpoint=8,Seed_Count=len(values),
                                 Actual_RUL=actual,XGBoost_RUL=xv,LSTM_Mean_RUL=values.mean(),
                                 LSTM_Min_RUL=values.min(),LSTM_Max_RUL=values.max()))
    save(fig,'04_forecasted_rul_distribution')
    summary=pd.DataFrame(distribution);summary.to_csv(OUT/'rul_distribution_summary.csv',index=False)

    # Plot ALL seven RUL approaches at ALL four shared-ML checkpoints.
    # This supplements (does not replace) the original checkpoint-8 distribution.
    fig,axes=plt.subplots(2,1,figsize=(11,8),constrained_layout=True)
    method_keys=['Linear (individual curve)','Exponential (individual curve)',
                 'Square-root cycle (individual curve)','Power law (individual curve)',
                 'Shared XGBoost','Minimal LSTM (window 1)','Minimal LSTM (window 3)']
    for ax,cell in zip(axes,CELLS):
        g=rul_all[(rul_all.Dataset_ID==cell)&rul_all.Checkpoint.isin([5,8,10,12])]
        actual=g.groupby('Checkpoint').Actual_RUL.first().sort_index()
        ax.plot(actual.index,actual.values,'k--o',lw=2,label='Observed relative RUL')
        for model in method_keys:
            f=g[g.Method==model].groupby('Checkpoint').Predicted_RUL.mean().sort_index()
            if not f.empty:
                ax.plot(f.index,f.values,marker='o',markersize=4,label=model.replace(' (individual curve)',''))
        ax.set(title=f'Cell {cell}: all seven approaches',xlabel='Observed checkpoint cycle',ylabel='Predicted RUL (cycles)',xticks=[5,8,10,12])
        ax.grid(alpha=.25)
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,ncol=4,loc='lower center',bbox_to_anchor=(.5,-.04),fontsize=8)
    save(fig,'05_all_rul_models_checkpoints')

    manifest=dict(source_sha256={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in SOURCES},
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  distribution_checkpoint=8,all_model_checkpoints=[5,8,10,12],seeds=[42,7,123],rul_reference='80% of first valid measured capacity (cycle 2)')
    (OUT/'visualization_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(summary.to_string(index=False))
    print(f"Figures and provenance saved to {OUT}")


if __name__=='__main__':main()
