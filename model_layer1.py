#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yaxiang Layered Stock Selection Model v1.0
Layer 1: Fundamental Filter | Layer 2: V4 Timing
"""
import akshare as ak, pandas as pd, numpy as np, json, sys, io, time
from datetime import datetime
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
OUT = Path(__file__).parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

CANDIDATES = [
    ("300308","ZhongJiXuChuang","Optic Module #1",5),
    ("601138","GongYeFuLian","AI Server OEM",5),
    ("603929","YaXiangJiCheng","Cleanroom Sole",5),
    ("002916","ShenNanDianLu","IC Substrate Sole",5),
    ("002281","GuangXunKeJi","Optical Chip",4),
    ("002837","YingWeiKe","Liquid Cooling",4),
    ("002851","MaiGeMiTe","AI Power NVDA",5),
    ("002409","YaKeKeJi","HBM Precursor",4),
    ("600584","ChangDianKeJi","CoWoS Package",4),
    ("600183","ShengYiKeJi","High-Speed CCL",4),
    ("603986","ZhaoYiChuangXin","NOR Flash MCU",4),
    ("300476","ShengHongKeJi","AI Server PCB",3),
    ("300274","YangGuangDianYuan","Inverter #1",5),
    ("300474","JingJiaWei","Sole GPU",5),
    ("301269","HuaDaJiuTian","Sole EDA",5),
    ("688981","ZhongXinGuoJi","Sole Foundry",5),
    ("002475","LiXunJingMi","Connector Leader",3),
    ("300124","HuiChuanJiShu","AI Servo",4),
    ("688012","ZhongWeiGongSi","Etching Sole",5),
    ("002371","BeiFangHuaChuang","Equipment Plat",4),
    ("688008","LanQiKeJi","DDR5 Interface",5),
    ("688256","HanWuJi","AI Chip Sole",5),
    ("300502","XinYiSheng","800G Module",4),
    ("002156","TongFuWeiDian","AMD Package",4),
    ("002436","XingSenKeJi","FCBGA Substrate",4),
    ("300394","TianFuTongXin","Optical Engine",4),
    ("688041","HaiGuangXinXi","CPU DCU Sole",5),
    ("688268","HuaTeQiTi","Electronic Gas",3),
    ("688234","TianYueXianJin","SiC Substrate",4),
    ("002428","YunNanZheYe","InP Substrate",4),
    ("300346","NanDaGuangDian","MO Source PR",4),
    ("688629","HuaFengKeJi","High-Speed Conn",4),
    ("688668","DingTongKeJi","I/O Connector",3),
    ("603738","TaiJingKeJi","Crystal Osc",3),
    ("300661","ShengBangGuFen","Power IC",3),
]

def zscore(s,w=20):r=s.rolling(w,min_periods=w);mu=r.mean();sd=r.std().replace(0,np.nan);return (s-mu)/sd
def i1(d):d=d.copy();d["r20"]=d["close"].pct_change(20);d["ps"]=zscore(d["r20"],20);d["a5"]=d["amount"].rolling(5).mean();d["ar"]=d["amount"]/d["a5"].replace(0,np.nan);d["ifl"]=d["pct_chg"]*d["ar"];d["ifs"]=d["ifl"].rolling(5).mean();d["tz"]=zscore(d["turnover"]);av2=(d["high"]-d["low"])/d["close"].shift(1);d["az"]=zscore(av2);d["ls"]=((d["tz"]>2)&(d["az"]>2)).astype(int);d["ir"]=(d["ps"].fillna(0)*0.35+d["ifs"].fillna(0)*0.40+d["ls"].fillna(0)*0.25).rolling(5).mean().fillna(0);return d[["date","ir"]]
def i2(d):d=d.copy();d["rs"]=d["close"].pct_change(5);d["rm"]=d["close"].pct_change(20);d["rl"]=d["close"].pct_change(60);d["ms"]=zscore(2*d["rs"].fillna(0)-d["rm"].fillna(0)-d["rl"].fillna(0));dr=d["close"].pct_change();vs=dr.rolling(5).std();vl=dr.rolling(20).std();d["vt"]=zscore(vs/vl.replace(0,np.nan)-1);d["or_"]=d["open"]/d["close"].shift(1)-1;d["or"]=np.where(d["pct_chg"].abs()>0.001,d["or_"]/d["pct_chg"].replace(0,np.nan),0);d["ors"]=zscore(d["or"].rolling(10).mean());d["tr"]=(d["ms"].fillna(0)*0.35+d["vt"].fillna(0)*0.30+d["ors"].fillna(0)*0.35).rolling(5).mean().fillna(0);return d[["date","tr"]]
def i3(d):d=d.copy();d["am_"]=(d["pct_chg"].abs()/(d["amount"]/1e8)).replace([np.inf,-np.inf],np.nan);d["af"]=zscore(d["am_"].rolling(10).mean());d["t20"]=d["turnover"].rolling(20).mean();d["ts20"]=d["turnover"].rolling(20).std().replace(0,np.nan);d["tzs"]=(d["turnover"]-d["t20"])/d["ts20"];d["tf"]=-zscore(d["tzs"]);av3=(d["high"]-d["low"])/d["close"].shift(1);d["pi"]=(av3/(d["turnover"]+0.01)).replace([np.inf,-np.inf],np.nan);d["ipf"]=zscore(d["pi"].rolling(10).mean());d["lr"]=(d["af"].fillna(0)*0.40+d["tf"].fillna(0)*0.35+d["ipf"].fillna(0)*0.25).rolling(5).mean().fillna(0);return d[["date","lr"]]
def i4(d):d=d.copy();d["ret"]=d["close"].pct_change();d["r5"]=d["close"].pct_change(5);d["rv"]=-zscore(d["r5"]);pc=d["pct_chg"].fillna(0);th=pc.rolling(60).quantile(0.90);d["eu"]=(pc>th.fillna(2)).astype(int);d["lb"]=(d["ret"].rolling(3).mean()*d["eu"].shift(1)).rolling(3).mean();d["lf"]=zscore(d["lb"]);cr=d["close"].pct_change(20).fillna(0);d["itm"]=(cr>0.05).astype(float);d["il"]=(cr<-0.05).astype(float);d["dp"]=(d["itm"]*(-d["r5"].fillna(0))+d["il"]*d["r5"].fillna(0)).rolling(5).mean();d["dpf"]=zscore(d["dp"]);d["br"]=(d["rv"].fillna(0)*0.35+d["lf"].fillna(0)*0.30+d["dpf"].fillna(0)*0.35).rolling(5).mean().fillna(0);return d[["date","br"]]
def i5(d):d=d.copy();pc=d["pct_chg"].fillna(0);th=pc.rolling(60).quantile(0.90);d["eu"]=(pc>th.fillna(2)).astype(float);d["tz"]=zscore(d["turnover"]);lc=np.where(d["eu"]==1,-d["tz"].fillna(0),0);d["lc"]=zscore(pd.Series(lc).rolling(3).mean());dd5=d["close"].rolling(5).min()/d["close"].rolling(5).max()-1;nf=np.where(dd5.fillna(0)<-0.05,-dd5.fillna(0),0);d["nf"]=zscore(pd.Series(nf));d["mp"]=(d["pct_chg"]*d["amount"]/d["amount"].rolling(20).mean()).rolling(5).mean();d["mf"]=zscore(d["mp"]);d["nr"]=(d["lc"].fillna(0)*0.35+d["nf"].fillna(0)*0.25+d["mf"].fillna(0)*0.40).rolling(5).mean().fillna(0);return d[["date","nr"]]

def layer1_financial_filter(code):
    try:
        fin = ak.stock_financial_abstract(symbol=str(code))
        def gm(n,c):
            r=fin[fin["indicators"]==n] if "indicators" in fin.columns else fin[fin["indicators"]==n]
            # Try both naming conventions
            for col_name in ["indicators", "indicators"]:
                if col_name in fin.columns:
                    r=fin[fin[col_name]==n]
                    break
            if len(r)==0:
                r=fin[fin.iloc[:,1]==n]
            if len(r)>0 and c in r.columns:
                v=r.iloc[0][c];return float(v) if pd.notna(v) else 0
            return 0
        # Use direct column access
        np_y=0; np_q1=0; np_q1_25=0; np_py=0; ocf=0; eps=0; rev_y=0
        for _, row in fin.iterrows():
            ind = str(row.get("indicators", row.iloc[1]))
            if ind == "gui mu jin li run":
                np_y = float(row["20251231"])/1e8 if pd.notna(row.get("20251231",0)) else 0
                np_q1 = float(row["20260331"])/1e8 if pd.notna(row.get("20260331",0)) else 0
                np_q1_25 = float(row["20250331"])/1e8 if pd.notna(row.get("20250331",0)) else 0
                np_py = float(row["20241231"])/1e8 if pd.notna(row.get("20241231",0)) else 0
            if ind == "jing ying xian jin liu liang jing e":
                ocf = float(row["20251231"])/1e8 if pd.notna(row.get("20251231",0)) else 0
            if ind == "ji ben mei gu shou yi":
                eps = float(row["20251231"]) if pd.notna(row.get("20251231",0)) else 0
        if np_y==0 and eps==0:
            # Fallback: try column indices
            for _, row in fin.iterrows():
                ind = str(row.iloc[1])
                if "profit" in ind.lower() or "benefit" in ind.lower():
                    if "gui mu" in ind.lower():
                        np_y=float(row.iloc[2])/1e8 if len(row)>2 and pd.notna(row.iloc[2]) else 0
                        np_q1=float(row.iloc[2])/1e8 if len(row)>2 and pd.notna(row.iloc[2]) else 0
                if "cash" in ind.lower() or "flow" in ind.lower():
                    ocf=float(row.iloc[2])/1e8 if len(row)>2 and pd.notna(row.iloc[2]) else 0
        np_g = (np_y/np_py-1)*100 if np_py>0 else 0
        shares = np_y*1e8/eps if eps>0 else 0
        exch = "sh" if str(code).startswith("6") else "sz"
        df = ak.stock_zh_a_daily(symbol=exch+str(code), start_date="20260620", end_date="20260625", adjust="qfq")
        price = float(df["close"].iloc[-1])
        mcap = price*shares/1e8 if shares>0 else 0
        np_ttm = np_q1+np_y-np_q1_25
        fwd_np = np_q1*4
        pe = mcap/np_ttm if np_ttm>0 else 0
        fwd_pe = mcap/fwd_np if fwd_np>0 else 0
        peg = pe/np_g if pe>0 and np_g>0 else 99
        ocf_np = ocf/np_y if np_y>0 else 0
        return {"code":code,"price":round(price,2),"mcap":round(mcap,1),"np_y":round(np_y,2),"np_q1":round(np_q1,2),"np_g":round(np_g,1),"ocf_np":round(ocf_np,2),"pe":round(pe,1),"fwd_pe":round(fwd_pe,1),"peg":round(peg,2)}
    except Exception as e:
        return {"code":code,"error":str(e)[:60]}

def v4_signal(code):
    exch = "sh" if str(code).startswith("6") else "sz"
    try:
        df = ak.stock_zh_a_daily(symbol=exch+str(code), start_date="20240101", end_date="20260625", adjust="qfq")
        d = df.copy().sort_values("date").reset_index(drop=True); d["pct_chg"] = d["close"].pct_change()*100
        f1=i1(d); f2=i2(d); f3=i3(d); f4=i4(d); f5=i5(d)
        m = f1.merge(f2,on="date").merge(f3,on="date").merge(f4,on="date").merge(f5,on="date")
        for c in ["ir","tr","lr","br","nr"]: m[c+"_n"] = zscore(m[c],20)
        w = {"ir":0.25,"tr":0.20,"lr":0.20,"br":0.20,"nr":0.15}
        m["rs"] = sum(w[k]*m[k+"_n"].fillna(0) for k in w); m["rz"] = zscore(m["rs"],20)
        m["sig"] = 0; m.loc[m["rz"]>1.5,"sig"] = 1; m.loc[m["rz"]<-1.5,"sig"] = -1
        last = m.iloc[-1]; si = int(last["sig"])
        st = {1:"BUY",-1:"SELL",0:"HOLD"}[si]
        return {"signal":si,"signal_text":st,"zscore":round(float(last["rz"]),3),"price":round(float(d["close"].iloc[-1]),2)}
    except:
        return {"signal":0,"signal_text":"HOLD","zscore":0,"price":0}

print("="*70)
print("Yaxiang Layered Model v1.0 - Running on GitHub Actions")
print(f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"Candidates: {len(CANDIDATES)}")
print("="*70)

# Layer 1
l1_results = []
for code,name,desc,rarity in CANDIDATES:
    r = layer1_financial_filter(code)
    if "error" in r:
        print(f"  {name}: FAIL - {r['error']}")
        continue
    r["name"]=name; r["rarity"]=rarity
    ocs=3 if r["ocf_np"]>1.2 else (2 if r["ocf_np"]>0.8 else (1 if r["ocf_np"]>0.5 else 0))
    pgs=3 if r["peg"]<0.8 else (2 if r["peg"]<1.5 else (1 if r["peg"]<3.0 else 0))
    gs=3 if r["np_g"]>50 else (2 if r["np_g"]>20 else (1 if r["np_g"]>0 else 0))
    r["score"] = round(ocs*0.30 + pgs*0.25 + gs*0.25 + rarity*0.20, 2)
    r["pass"] = ocs>=2 and pgs>=2 and gs>=2
    l1_results.append(r)
    print(f"  {name}: OCF={r['ocf_np']:.2f} PEG={r['peg']:.2f} G={r['np_g']:.0f}% PASS={r['pass']}")
    time.sleep(0.5)

l1_passed = [r for r in l1_results if r["pass"]]
l1_passed.sort(key=lambda x:x["score"], reverse=True)

print(f"
Layer1 passed: {len(l1_passed)}/{len(l1_results)}")

# Layer 2
print(f"
Layer 2: V4 signals for passed stocks")
l2_results = []
for r in l1_passed:
    v4 = v4_signal(r["code"])
    r.update(v4)
    l2_results.append(r)
    print(f"  {r['name']}: {v4['signal_text']} z={v4['zscore']:+0.3f}")
    time.sleep(0.3)

# Report
rep = {"date":str(datetime.now()),"total_candidates":len(CANDIDATES),
       "layer1_passed":len(l1_passed),"layer1_failed":len(l1_results)-len(l1_passed),
       "summary":{"buy":len([r for r in l2_results if r.get("signal")==1]),
                  "hold":len([r for r in l2_results if r.get("signal")==0]),
                  "sell":len([r for r in l2_results if r.get("signal")==-1])},
       "recommendations":l2_results}
with open(OUT/"full_report.json","w",encoding="utf-8") as f:
    json.dump(rep,f,ensure_ascii=False,indent=2)
print(f"
Report saved: {OUT}/full_report.json")
print("Done")


