"""Build a five-page technical report from current pipeline result tables."""
from pathlib import Path
from html import escape
import shutil
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'scripts/outputs'
DEST = ROOT / 'output/pdf/Technical_Report_Module_Outputs.pdf'
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
def main():
    gold=pd.read_csv(OUT/'03_gold_cycle_features/battery_cycle_features_gold.csv',dtype={'Dataset_ID':str})
    fade=pd.read_csv(OUT/'04_capacity_fade/cycle_capacity_analysis.csv',dtype={'Dataset_ID':str})
    metrics=pd.read_csv(OUT/'11_rul_model_comparison/all_method_common_metrics.csv',dtype={'Dataset_ID':str})
    anomaly=pd.read_csv(OUT/'07_anomaly_detection/dbscan_labels.csv',dtype={'Dataset_ID':str})
    pack=pd.read_csv(OUT/'13_pack_scaling/scenario_summary.csv',dtype={'Dataset_ID':str})
    evaluation=pd.read_csv(OUT/'04_capacity_fade/evaluation_metrics.csv',dtype={'Dataset_ID':str})
    dvdq_summary=pd.read_csv(OUT/'06_differential_voltage/feature_cycle_summary.csv',dtype={'cell':str})
    rows=[]
    for cell,g in fade.groupby('Dataset_ID'):
        g=g.sort_values('Cycle_Index'); q=float(g.loc[g.Cycle_Index.eq(2),'Discharge_Capacity_Ah'].iloc[0]); below=g.loc[g.Discharge_Capacity_Ah.lt(.8*q),'Cycle_Index']
        rows.append([cell, f'{q:.4f}', f'{.8*q:.4f}', str(int(below.iloc[0])) if len(below) else 'Not observed'])
    st=[]
    def add(*x): st.extend(x)
    def page(title):
        if st: add(PageBreak())
        add(para(title,'Heading1'),Spacer(1,5))
    page('1 | Data engineering and scope')
    add(para('Two laboratory cell datasets were processed from their source Excel workbooks. Measurements are retained in source order; the pipeline records clock, missing-value, phase, coverage and counter diagnostics. Temperature is missing. The two cells have different operating currents and are not a matched population.'))
    add(para('The Bronze stage normalizes timestamps and validates the source schema. Silver assigns charge, discharge and rest phases and retains row-level flags. Gold integrates current and voltage within valid phase intervals, avoiding cross-phase integration. It calculates charge and discharge capacity, charge C-rate using provisional 2.5 Ah, cycle duration, energy throughput and diagnostic coulombic efficiency. Completeness, measurement coverage, counter agreement and protocol verification are distinct quality checks.'))
    add(para('Missing temperature is not imputed; anomalous measurements and clock reversals remain visible for review. Counter comparisons and time coverage support the numerical integrations but do not prove that the physical cycling protocol was complete.'))
    add(table(['Cell','Cycle 2 (Ah)','Relative 80% (Ah)','First below'],rows,[95,115,140,140]))
    declines=[]
    for cell,g in fade.groupby('Dataset_ID'):
        g=g.sort_values('Cycle_Index'); first=float(g.loc[g.Cycle_Index.eq(2),'Discharge_Capacity_Ah'].iloc[0]); last=float(g.loc[g.Cycle_Index.eq(100),'Discharge_Capacity_Ah'].iloc[0])
        declines.append(f'{escape(str(cell))}: {first:.3f} to {last:.3f} Ah ({100*(1-last/first):.1f}% decline)')
    add(para('Measured high-current discharge capacity, cycle 2 to 100: ' + '; '.join(declines) + '.'))
    add(para('The reported EOL is the first observed crossing of 80% of cycle-2 high-current delivered capacity. This is an exploratory relative endpoint. Nominal capacity and reference conditions are unverified; at the provisional 2.5 Ah nominal rating, 80% is 2.0 Ah and both cells are already below it at cycle 2. A nominal-threshold crossing cannot be dated from these complete observations.'))
    page('2 | Capacity fade and efficiency')
    add(figure(Path('14_reporting_visualization/01_capacity_predictive_curves.png'),height=185))
    add(para('Capacity against cycle count with linear, exponential, square-root elapsed-time and power-law descriptive fits. Full-history curves summarize observed behaviour and are not early forecasts. Extrapolated negative capacities, where present, are not physically meaningful.','CaptionSmall'))
    add(figure(Path('14_reporting_visualization/02_coulombic_efficiency.png'),height=185))
    add(para('Diagnostic coulombic efficiency is integrated discharge capacity divided by charge capacity. Values above 100% are retained and flagged; protocol pairing, current integration and measurement uncertainty must be reviewed before interpreting them as electrochemical behaviour. C-rate and energy estimates inherit the provisional rating and measurement-quality limits.','CaptionSmall'))
    add(para('The comparison includes statistical regression, a physics-inspired phenomenological surrogate and an LSTM baseline evaluated chronologically. The physics-inspired form is a modelling constraint, not proof of a particular degradation mechanism.'))
    best=evaluation[(evaluation.Scope=='validation') & (evaluation.Model!='Fixed-origin persistence')].sort_values('RMSE_Ah').groupby('Dataset_ID',sort=True).first()
    add(para('Lowest empirical validation RMSE: ' + '; '.join(f'{escape(str(cell))}: {escape(str(row.Model))}, {row.RMSE_Ah:.4f} Ah' for cell,row in best.iterrows()) + '. The split is chronological; it does not validate extrapolation to unseen cells.'))
    page('3 | Degradation signatures and anomalies')
    add(figure(Path('14_reporting_visualization/03_deviation_clusters.png'),height=215))
    add(para('Exponential residuals and local deviations identify review candidates; DBSCAN uses robustly scaled residual, change and efficiency features. A noise label is an unsupervised screening result, not a confirmed fault or diagnosis. Sensitivity to clustering settings is reported in the analysis outputs.','CaptionSmall'))
    add(para('Differential voltage analysis integrates discharge current, interpolates voltage against discharged capacity, smooths curves and compares interior dV/dQ minima across smoothing windows and neighbouring cycles. Since discharged Q is positive, voltage generally falls and dV/dQ is negative; candidates are peaks in -dV/dQ. A near-zero derivative corresponds to a voltage plateau.'))
    counts=dvdq_summary.groupby('cell')[['candidate_count','stable_count']].sum()
    add(para('Across the six selected cycles, candidates and heuristic repeatable detections are: ' + '; '.join(f'{escape(str(cell))}: {int(row.candidate_count)} and {int(row.stable_count)}' for cell,row in counts.iterrows()) + '. Repetition is a sensitivity check, not a verified cross-cycle feature identity.'))
    add(figure(Path('06_differential_voltage/feature_candidates_by_cycle.png'),height=175))
    add(para('Unconnected points show candidate position and half-prominence width; no electrode identity or causal trajectory is inferred. High current, polarization, sampling and smoothing prevent unique LLI/LAM attribution.','CaptionSmall'))
    page('4 | Remaining useful life')
    add(figure(Path('14_reporting_visualization/04_forecasted_rul_distribution.png'),height=185))
    add(para('Early forecasts use only history through the stated checkpoint. Per-cell curve extrapolation is compared with pooled feature-based XGBoost and minimal LSTM sequence models. Training uses both cells, so this is not independent unseen-cell validation. Attempts that never cross within the horizon are retained as failures; error metrics must be interpreted with coverage.','CaptionSmall'))
    subset=metrics[metrics.Method.isin(['Exponential (individual curve)','Shared XGBoost','Minimal LSTM (window 3)'])]
    mr=[[r.Dataset_ID,r.Method,f'{r.MAE_Cycles:.2f}' if pd.notna(r.MAE_Cycles) else 'NA',f'{r.Scored}/{r.Attempts}'] for r in subset.itertuples()]
    add(table(['Cell','Method, common checkpoints','MAE cycles','Scored/attempts'],mr,[60,255,80,95]))
    add(para('The displayed model-seed spread is not a calibrated population RUL distribution or a confidence interval. Only two cells and a handful of early training windows are available; external validation and more cells across conditions are needed.'))
    page('5 | Module, pack and fleet implications')
    add(para('The synthetic 12S2P scenario groups cells into series-connected parallel pairs. Sampled initial-capacity and fade-rate variation, assumed Arrhenius temperature acceleration, and simplified passive or active balancing affect a capacity envelope. Scenario inputs are illustrative and are not fitted fleet distributions or measured pack performance.'))
    selected=pack[pack.Scenario.isin(['uniform_no_balance','gradient_no_balance','gradient_passive','gradient_active'])]
    pr=[[r.Dataset_ID,r.Scenario,f'{r.Mean_EOL:.1f}',f'{r.Mean_Initial_Balance_Loss_Wh:.2f}'] for r in selected.itertuples()]
    add(table(['Cell baseline','Scenario','Mean EOL cycle','Initial loss Wh'],pr,[90,210,100,90]))
    add(para('The envelope is computationally inexpensive for Monte Carlo studies but omits coupled thermal dynamics, resistance growth, voltage cutoff, current sharing and a calibrated BMS. More detailed electrothermal and balancing models improve physical coverage at higher calibration and computational cost; a validated surrogate can support larger fleets.'))
    add(para('Next steps: collect matched-cell capacity, impedance, temperature and balancing measurements; verify nominal ratings and protocol; validate predictions on unseen cells and packs; and quantify uncertainty and censoring. Fleet and battery-passport records should carry test conditions, provenance, SOH definition, model version, uncertainty and applicable reporting requirements.'))
    def footer(canvas,doc):
        canvas.setFont('Helvetica',8);canvas.drawString(48,28,'Exploratory two-cell study | relative capacity endpoint');canvas.drawRightString(547,28,f'{doc.page} / 5')
    DEST.parent.mkdir(parents=True,exist_ok=True)
    SimpleDocTemplate(str(DEST),pagesize=(595.28,841.89),leftMargin=48,rightMargin=48,topMargin=40,bottomMargin=50).build(st,onFirstPage=footer,onLaterPages=footer)
    pages=len(PdfReader(str(DEST)).pages)
    if pages != 5: raise RuntimeError(f'Expected 5 pages, got {pages}')
    shutil.copyfile(DEST, ROOT / 'Technical_Report.pdf')
    print(f'Created {DEST} ({pages} pages)')
if __name__=='__main__': main()
