"""Build a five-page technical report from current pipeline result tables."""

# Make shared task modules importable when running this file directly.
import sys as _task_sys
from pathlib import Path as _TaskPath
_task_scripts = _TaskPath(__file__).resolve().parents[1]
for _task_dir in ("task1_data_engineering", "task2_degradation_modeling", "task3_anomaly_detection", "task4_rul_estimation", "task5_pack_scaling", "task6_reporting"):
    _task_path = str(_task_scripts / _task_dir)
    if _task_path not in _task_sys.path:
        _task_sys.path.append(_task_path)

from pathlib import Path
from html import escape
import shutil
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
_task_sys.path.append(str(_task_scripts))
from output_paths import TaskOutputs
OUT = TaskOutputs()
DEST = ROOT / 'scripts/task6_reporting/outputs/Technical_Report.pdf'
S = getSampleStyleSheet()
S.add(ParagraphStyle(name='BodySmall', fontName='Helvetica', fontSize=8.5, leading=11.5, spaceAfter=6))
S.add(ParagraphStyle(name='CaptionSmall', fontName='Helvetica', fontSize=7.5, leading=10, textColor=colors.HexColor('#526574'), spaceAfter=6))
S['Heading1'].textColor = colors.HexColor('#17486b')
def para(text, style='BodySmall'):
    return Paragraph(text, S[style])
def table(headers, rows, widths):
    data = [[para(escape(str(v)), 'CaptionSmall') for v in row] for row in [headers] + rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eaf1f5')), ('GRID',(0,0),(-1,-1),.3,colors.lightgrey), ('VALIGN',(0,0),(-1,-1),'TOP')]))
    return t
def figure(path, width=490, height=180):
    path=OUT/path
    w,h=ImageReader(str(path)).getSize(); scale=min(width/w,height/h)
    return Image(str(path),width=w*scale,height=h*scale)
def head2(text):
    return Paragraph(f'<b>{escape(text)}</b>', S['BodySmall'])

def main():
    gold=pd.read_csv(OUT/'03_gold_cycle_features/battery_cycle_features_gold.csv',dtype={'Dataset_ID':str})
    fade=pd.read_csv(OUT/'04_capacity_fade/cycle_capacity_analysis.csv',dtype={'Dataset_ID':str})
    metrics=pd.read_csv(OUT/'11_rul_model_comparison/all_method_common_metrics.csv',dtype={'Dataset_ID':str})
    anomaly=pd.read_csv(OUT/'07_anomaly_detection/dbscan_labels.csv',dtype={'Dataset_ID':str})
    pack=pd.read_csv(OUT/'13_pack_scaling/scenario_summary.csv',dtype={'Dataset_ID':str})
    evaluation=pd.read_csv(OUT/'04_capacity_fade/evaluation_metrics.csv',dtype={'Dataset_ID':str})
    dvdq_summary=pd.read_csv(OUT/'06_differential_voltage/feature_cycle_summary.csv',dtype={'cell':str})
    eol_rows=[]
    for cell,g in fade.groupby('Dataset_ID'):
        g=g.sort_values('Cycle_Index'); q=float(g.loc[g.Cycle_Index.eq(2),'Discharge_Capacity_Ah'].iloc[0]); below=g.loc[g.Discharge_Capacity_Ah.lt(.8*q),'Cycle_Index']
        eol_rows.append([cell, f'{q:.4f}', f'{.8*q:.4f}', str(int(below.iloc[0])) if len(below) else 'Not observed'])
    st=[]
    def add(*x): st.extend(x)
    def page(title):
        if st: add(PageBreak())
        add(para(title,'Heading1'),Spacer(1,4))

    # ── PAGE 1: Data Engineering ──────────────────────────────────────────────
    page('1 | Data Engineering — Bronze → Silver → Gold')
    add(head2('Scope'))
    add(para('Two LR1865SZ laboratory cells (001_2, 002_4) with 99 complete discharge cycles each (cycles 2–100). The cells have different operating currents and are not a matched population. Temperature is absent from both datasets.'))
    add(head2('Method'))
    add(para('<b>Bronze</b> — Reads source Excel workbooks; validates 9 required schema columns; applies 22 per-row quality checks (timestamp gaps/reversals, voltage/current plausibility, counter resets, duplicate rows, cycle-index jumps). Every row is retained with a REJECTED/FLAGGED/OK status and a quality_flags string. Anomalous measurements are not silently removed.'))
    add(para('<b>Silver</b> — Assigns charge, discharge, and rest phase labels from current sign (deadband 0.005 A). Checks phase continuity and counter agreement per cycle.'))
    add(para('<b>Gold</b> — Trapezoidal current integration within valid intervals (same phase, 0 &lt; dt ≤ 5 s, no artifact, no timestamp reversal). Derives per-cycle: Discharge_Capacity_Ah, Charge_Capacity_Ah, Coulombic_Efficiency_pct, Discharge_Energy_Wh, duration, C-rate (mean and P99). Marks Computationally_Complete and Discharge_Integration_Valid.'))
    add(head2('Key results'))
    add(table(['Cell','Cycle-2 discharge (Ah)','80 % threshold (Ah)','First cycle below 80 %'],eol_rows,[110,120,120,130]))
    declines=[]
    for cell,g in fade.groupby('Dataset_ID'):
        g=g.sort_values('Cycle_Index'); first=float(g.loc[g.Cycle_Index.eq(2),'Discharge_Capacity_Ah'].iloc[0]); last=float(g.loc[g.Cycle_Index.eq(100),'Discharge_Capacity_Ah'].iloc[0])
        declines.append(f'{escape(str(cell))}: {first:.3f}→{last:.3f} Ah (−{100*(1-last/first):.1f} %)')
    add(para('Capacity cycle 2 to 100: ' + '; '.join(declines) + '.'))
    add(head2('Limitations'))
    add(para('Temperature missing throughout; thermal analysis is impossible. Nominal capacity (2.5 Ah) is provisional — both cells are already below 80 % of nominal at cycle 2, so a nominal-threshold EOL cannot be dated from these records. Voltage "outside plausible" bounds (2.5/4.3 V) are hardcoded in Bronze rather than read from config — both are currently correct but would diverge if config is updated. The cycle_elapsed_s groupby uses unvalidated cycle indices; NaN cycle indices would be silently excluded.'))

    # ── PAGE 2: Capacity Fade & Efficiency ────────────────────────────────────
    page('2 | Capacity Fade Modeling and Coulombic Efficiency')
    add(head2('Method'))
    add(para('Four models fitted to cycles 2–100 (n = Cycle_Index − 2): Linear Q = q0 − a·n; Exponential Q = q0·exp(−k·n), k ∈ [0, 0.2]; Square-root time Q = q0 − a·√t; Power law Q = q0 − a·n<super>b</super>, b ∈ [0.05, 2]. Profile least squares closes q0/a analytically; nonlinear exponents are found by dense grid search with five iterative refinements. Chronological split: train 2–70, validate 71–85, refit 2–85, test 86–100.'))
    add(figure(Path('14_reporting_visualization/01_capacity_predictive_curves.png'),height=165))
    add(para('Figure 1. Measured discharge Ah (black dots) with four descriptive fit curves. Dashed line = 80 % of cycle-2 capacity; dotted vertical = observed EOL; red point = EOL measurement. Full-history curves are retrospective summaries, not early forecasts.','CaptionSmall'))
    add(figure(Path('14_reporting_visualization/02_coulombic_efficiency.png'),height=150))
    add(para('Figure 2. Coulombic efficiency (%) = 100 × Q_discharge / Q_charge per cycle. Flagged cycles (CE > 100 %) are annotated; these are review candidates — protocol pairing or integration artefacts rather than confirmed electrochemical events.','CaptionSmall'))
    add(head2('Key results'))
    best=evaluation[(evaluation.Scope=='validation') & (evaluation.Model!='Fixed-origin persistence')].sort_values('RMSE_Ah').groupby('Dataset_ID',sort=True).first()
    vrows=[[cell, row.Model, f'{row.RMSE_Ah:.4f}', f'{row.R2:.3f}'] for cell,row in best.iterrows()]
    add(table(['Cell','Winning model (val RMSE)','Val RMSE (Ah)','Full-series R²'],vrows,[80,185,100,105]))
    add(para('001_2 Exponential full-series: q0=1.432 Ah, k=0.0195/cycle, R²=0.987. 002_4: q0=1.764 Ah, k=0.0145/cycle, R²=0.994. Test R² is negative for most models — persistence outperforms extrapolation on the narrow 15-cycle test window.'))
    add(head2('Limitations'))
    add(para('Fade_Rate_Ah_per_Cycle_Smoothed follows ΔQ sign (negative = fade); the unsmoothed Fade_Rate_Ah_per_Cycle uses −ΔQ (positive = fade). The sign convention differs between columns. Square-root time model uses future timestamps and is excluded from live-forecast winner selection. High-current polarization and changing charge endpoints are conflated with ageing in all fits.'))

    # ── PAGE 3: Anomalies & dV/dQ ─────────────────────────────────────────────
    page('3 | Degradation Signatures and Anomaly Detection')
    add(head2('Method — Anomaly detection'))
    add(para('(1) Exponential residuals: fits Q = q0·exp(−k·n) to cycles 2–100; computes Capacity_Residual_Ah = observed − fitted; flags |robust z| > 3. (2) Local deviation: flags cycles where |Q_n − mean(Q_{n−1}, Q_{n+1})| is unusually large (|local z| > 3). (3) Trend candidate: requires both flags simultaneously; neither cell produced any. (4) DBSCAN on three robustly scaled features (detrended residual, change deviation, CE deviation); eps=0.8, min_samples=5; label −1 = anomalous noise.'))
    add(figure(Path('14_reporting_visualization/03_deviation_clusters.png'),height=200))
    add(para('Figure 3. Upper panels: DBSCAN feature scatter (detrended residual vs. change deviation); red × = noise label. Lower panels: same noise cycles located on the capacity trajectory.','CaptionSmall'))
    add(head2('Key results — Anomalies'))
    add(para('001_2: 0 exponential flags; 9 local flags (cycles 4–6, 8–10, 12, 26, 27); 0 trend candidates; ~25/98 DBSCAN noise cycles. 002_4: 0 exponential flags; 0 local flags; 0 trend candidates; ~45/98 DBSCAN noise cycles. All 198 Gold cycles carry Quality_Status=REVIEW from upstream flags. DBSCAN noise fraction is parameter-sensitive: at eps=0.5 on 001_2, noise rises to 59/98.'))
    add(head2('Method — Differential voltage'))
    add(para('Selected discharge cycles (2, 10, 25, 50, 75, 100) plus neighbours. Integrates current→Q; interpolates V(Q) onto 301 capacity points; smooths with 11/21/31-point Savitzky-Golay windows; detects interior dV/dQ peaks (10–90 % of Q range). Stability criterion: peak present in all three windows AND in a neighbouring cycle.'))
    counts=dvdq_summary.groupby('cell')[['candidate_count','stable_count']].sum()
    add(para('dV/dQ results — candidates / stable detections: ' + '; '.join(f'{escape(str(cell))}: {int(row.candidate_count)} / {int(row.stable_count)}' for cell,row in counts.iterrows()) + '.'))
    add(head2('Limitations'))
    add(para('Local deviation cannot score the first or last cycle (no neighbour). A single anomalous cycle will also flag its immediate neighbours. DBSCAN results reported for one parameter set only. High discharge current causes polarization that changes peak positions independently of ageing — no electrode mechanism can be uniquely attributed. dV/dQ stability is a heuristic, not a cross-cycle feature identity.'))

    # ── PAGE 4: RUL Estimation ────────────────────────────────────────────────
    page('4 | Remaining Useful Life Estimation')
    add(head2('Method'))
    add(para('<b>Individual curve RUL:</b> at each checkpoint (5, 8, 10, 12), fits all four fade models to available history; extrapolates to first predicted crossing of 80 % threshold. No-crossing within 1,000 cycles = failure.'))
    add(para('<b>Shared XGBoost:</b> features = last 3 capacities, last/mean cycle-to-cycle changes, cycles since BOL. Trains on both cells pooled at each checkpoint; iterates predicted capacity changes until threshold crossed.'))
    add(para('<b>Minimal LSTM:</b> 1 hidden unit; sliding windows of size 1 or 3; 3 seeds (42, 7, 123). Normalises by own cycle-2 capacity; iterative forecast; horizon 1,000 cycles. Both cells in training set — not independent external validation.'))
    add(para('<b>Comparison:</b> primary fair evaluation at checkpoints 8 and 10 for four methods. All attempts retained including failures; MAE conditioned on scored attempts; coverage = fraction producing valid crossing prediction.'))
    add(figure(Path('14_reporting_visualization/04_forecasted_rul_distribution.png'),height=155))
    add(para('Figure 4. Checkpoint 8: bars = three LSTM seed outcomes (window=3); orange marker = XGBoost; black dashed = actual RUL. Seed counts are not a population distribution or confidence interval.','CaptionSmall'))
    add(head2('Key results (checkpoints 8 & 10)'))
    subset=metrics[metrics.Method.isin(['Exponential (individual curve)','Linear (individual curve)','Shared XGBoost','Minimal LSTM (window 3)'])]
    mr=[[r.Dataset_ID, r.Method.replace(' (individual curve)','').replace('Minimal ',''),
         f'{r.MAE_Cycles:.1f}' if pd.notna(r.MAE_Cycles) else 'NA',
         f'{r.Bias_Cycles:+.1f}' if pd.notna(r.Bias_Cycles) else 'NA',
         f'{r.Scored}/{r.Attempts}'] for r in subset.itertuples()]
    add(table(['Cell','Method','MAE (cyc)','Bias (cyc)','Scored/att'],mr,[55,185,65,65,60]))
    add(para('Power law overestimates 002_4 RUL by 11 cycles. Square-root cycle overestimates 002_4 by 47 cycles (uses future timestamps — do not use as forecast). LSTM window=1 achieves MAE 1.3 on 001_2 but −6.1 bias on 002_4 (systematic early prediction).'))
    add(head2('Limitations'))
    add(para('Both cells in XGBoost and LSTM training sets — results are descriptive, not generalisable. Only 4 checkpoints × 2 cells = 8 scored attempts per method. Actual EOL is 11 and 22 cycles; most checkpoints leave ≤ 14 cycles of history. LSTM has 1 hidden unit — a minimal proof-of-concept. Seed spread reflects initialisation sensitivity, not a population distribution.'))

    # ── PAGE 5: Pack Scaling, Fleet, Limitations ──────────────────────────────
    page('5 | Module/Pack Scaling, Fleet Analytics and Limitations')
    add(head2('Method — Pack scaling'))
    add(para('Synthetic 12S2P pack: 4 series groups × 2 parallel cells × 3 modules = 24 cells. Monte Carlo (E=100): lognormal capacity (CV=3 %) and rate (CV=15 %) draws centred on each cell\'s exponential fit. Linear 0–10 K temperature gradient with Arrhenius acceleration (Ea=20,000 J/mol, assumed). Four scenarios: uniform/gradient × no-balance/passive/active (η=85 %). Envelope: sum parallels, min series groups, min modules. EOL at pack/BOL &lt; 0.80.'))
    selected=pack[pack.Scenario.isin(['uniform_no_balance','gradient_no_balance','gradient_passive','gradient_active'])]
    pr=[[r.Dataset_ID, r.Scenario.replace('_',' '), f'{r.Mean_EOL:.1f}', f'{r.Mean_Initial_Balance_Loss_Wh:.2f}'] for r in selected.itertuples()]
    add(table(['Cell','Scenario','Mean EOL (cyc)','Balance loss (Wh)'],pr,[75,185,90,100]))
    add(para('Gradient cuts EOL by ~1.5 cycles (001_2) and ~3 cycles (002_4). Passive balancing bleeds usable charge (1.6 Wh loss) and underperforms active (0.07 Wh loss).','CaptionSmall'))
    add(head2('Fleet analytics and battery passport extensions'))
    add(para('To scale to a fleet: (1) replace assumed CVs with measured cell-population distributions; (2) replace Ea with chemistry-calibrated values (literature: 40,000–80,000 J/mol for Li-ion); (3) cluster-based surrogate — group cells into 5–10 DBSCAN clusters by thermal state and voltage residuals, run RUL inference only on cluster centroids. Reduces inference cost by >99 % vs. per-cell digital twin while retaining weakest-link sensitivity. Battery Passport records must carry: test conditions, provenance hash, SOH definition, model version, uncertainty bands, and applicable reporting standard.'))
    add(para('<i>Full methodology in outputs/13_pack_scaling/pack_scaling_methodology.md. §D–F summarised below.</i>','CaptionSmall'))
    add(head2('Module intermediate step (§D) | Pack RUL propagation (§E)'))
    add(para('<b>§D — Two-stage aggregation:</b> cell→module: Q_module = min_s[sum_p Q_{m,s,p}·SOC] per module independently (each module has its own thermal/balancing history). module→pack: Q_pack = min_m Q_module. Parallel-cell averaging reduces effective CV entering the series-minimum. Practically: flag a module for replacement when its P05 retention crosses 80 %, even if pack mean is above threshold; grade modules for second-life by (mean, variance) of remaining capacity.'))
    add(para('<b>§E — Pack RUL:</b> n_pack_EOL^(e) = min over all cells of n_cell_EOL^(e) per ensemble member. The minimum of N variables shifts left and narrows as N grows — pack RUL is shorter and more predictable than single-cell RUL. Report P05 (warranty), P50 (median), P95 (optimistic). Propagate LSTM uncertainty via bootstrap: retrain on B resamples, obtain B EOLs per cell, build pack EOL distribution from all B×N_cells predictions.'))
    add(head2('Degradation mode interactions (§F)'))
    add(para('<b>SEI growth:</b> spatially correlated within each thermal zone — use correlated lognormal sampling, not independent draws. <b>Lithium plating:</b> highest risk in the lowest-impedance parallel cell (current crowding), not the lowest-capacity cell; makes fast-charge degradation superlinear in pack size; detectable as dV/dQ anode staging peak loss. <b>Mechanical fatigue:</b> anti-correlates with balancing undercharge — chronically undercharged cells see smaller SOC swings and less particle cracking, partially compensating their electrochemical disadvantage.'))
    add(head2('Pipeline-wide limitations'))
    add(para('Two cells, different currents, no temperature, provisional 2.5 Ah rating, no external validation. Fade_Rate_Ah_per_Cycle_Smoothed sign is opposite to its unsmoothed counterpart. Pack Ea=20,000 J/mol underestimates thermal acceleration (use 40,000–80,000 J/mol). No voltage/OCV model or balancing heat feedback in simulation. assert len(g)==99 in stage_04 is brittle on reruns. Voltage plausibility bounds (2.5/4.3 V) hardcoded alongside config-driven spec bounds.'))

    def footer(canvas,doc):
        canvas.setFont('Helvetica',8)
        canvas.setFillColor(colors.HexColor('#526574'))
        canvas.drawString(48,28,'Battery degradation analysis | LR1865SZ two-cell study')
        canvas.drawRightString(547,28,f'Page {doc.page} of 5')
    DEST.parent.mkdir(parents=True,exist_ok=True)
    SimpleDocTemplate(str(DEST),pagesize=(595.28,841.89),leftMargin=48,rightMargin=48,topMargin=40,bottomMargin=50).build(st,onFirstPage=footer,onLaterPages=footer)
    pages=len(PdfReader(str(DEST)).pages)
    if pages != 5: raise RuntimeError(f'Expected 5 pages, got {pages}')
    (ROOT / 'output/pdf').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(DEST, ROOT / 'output/pdf/Technical_Report_Module_Outputs.pdf')
    shutil.copyfile(DEST, ROOT / 'Technical_Report.pdf')
    print(f'Created {DEST} ({pages} pages)')
if __name__=='__main__': main()
