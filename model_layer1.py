#!/usr/bin/env python3
"""
亚翔集成分层选股模型 v1.0
============================
Layer 1: 基本面筛选（低频, 季报更新）
Layer 2: V4时机判断（高频, 日频更新）

作者: Codex
日期: 2026-06-25
"""

import akshare as ak
import pandas as pd
import numpy as np
import json, sys, io, time
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ===================== 配置区 =====================
OUT = Path(__file__).parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

# 候选股票池（可自行增删）
CANDIDATES = [
    # (代码, 名称, 细分领域, 稀缺性评分1-5)
    ("300308","中际旭创","光模块(全球第一)",5),
    ("601138","工业富联","AI服务器代工",5),
    ("603929","亚翔集成","洁净室(唯一)",5),
    ("002916","深南电路","IC封装基板(唯一)",5),
    ("002281","光迅科技","光芯片(自研EML)",4),
    ("002837","英维克","AI液冷CDU",4),
    ("002851","麦格米特","AI电源(英伟达链)",5),
    ("002409","雅克科技","HBM前驱体",4),
    ("600584","长电科技","先进封装(CoWoS)",4),
    ("600183","生益科技","高频覆铜板(国内第一)",4),
    ("603986","兆易创新","NOR Flash+MCU",4),
    ("300476","胜宏科技","AI服务器PCB",3),
    ("300274","阳光电源","逆变器(全球第一)",5),
    ("300474","景嘉微","GPU(唯一)",5),
    ("301269","华大九天","EDA(唯一)",5),
    ("688981","中芯国际","晶圆代工(唯一)",5),
    ("002475","立讯精密","连接器龙头",3),
    ("300124","汇川技术","工控AI伺服",4),
    ("688012","中微公司","刻蚀设备(唯一)",5),
    ("002371","北方华创","半导体设备平台",4),
    ("688008","澜起科技","DDR5接口(唯一)",5),
    ("688256","寒武纪","AI芯片(唯一)",5),
    ("300502","新易盛","800G光模块",4),
    ("002156","通富微电","先进封装(AMD链)",4),
    ("002436","兴森科技","FCBGA封装基板",4),
    ("300394","天孚通信","光引擎",4),
    ("688041","海光信息","CPU+DCU(唯一)",5),
    ("688268","华特气体","电子特气",3),
    ("688234","天岳先进","SiC衬底",4),
    ("002428","云南锗业","磷化铟InP衬底",4),
    ("300346","南大光电","MO源+光刻胶",4),
    ("688629","华丰科技","高速背板连接器",4),
    ("688668","鼎通科技","I/O连接器",3),
    ("603738","泰晶科技","晶体振荡器",3),
    ("300661","圣邦股份","电源管理IC",3),
]

# ===================== Layer 1: 基本面筛选 =====================
def layer1_financial_filter(code):
    """获取单只股票的基本面指标"""
    try:
        fin = ak.stock_financial_abstract(symbol=str(code))
        def gm(n,c):
            r=fin[fin["指标"]==n]
            if len(r)>0 and c in r.columns:v=r.iloc[0][c];return float(v) if pd.notna(v) else 0
            return 0
        
        np_y=gm("归母净利润","20251231")/1e8
        np_q1=gm("归母净利润","20260331")/1e8
        np_q1_25=gm("归母净利润","20250331")/1e8
        np_py=gm("归母净利润","20241231")/1e8
        ocf=gm("经营现金流量净额","20251231")/1e8
        eps=gm("基本每股收益","20251231")
        rev_y=gm("营业总收入","20251231")/1e8
        
        # 净利增长
        np_g=(np_y/np_py-1)*100 if np_py>0 else 0
        # 总股本
        shares=np_y*1e8/eps if eps>0 else 0
        
        # 获取当前价格
        exch="sh" if str(code).startswith("6") else "sz"
        df=ak.stock_zh_a_daily(symbol=exch+str(code),start_date="20260620",end_date="20260625",adjust="qfq")
        price=float(df["close"].iloc[-1])
        mcap=price*shares/1e8 if shares>0 else 0
        
        # PE/PEG
        np_ttm=np_q1+np_y-np_q1_25
        fwd_np=np_q1*4
        pe=mcap/np_ttm if np_ttm>0 else 0
        fwd_pe=mcap/fwd_np if fwd_np>0 else 0
        peg=pe/np_g if pe>0 and np_g>0 else 99
        
        # OCF/NP
        ocf_np=ocf/np_y if np_y>0 else 0
        
        return {
            "code":code,"price":round(price,2),"mcap":round(mcap,1),
            "rev_y":round(rev_y,1),"np_y":round(np_y,2),"np_q1":round(np_q1,2),
            "np_g":round(np_g,1),"ocf":round(ocf,2),"ocf_np":round(ocf_np,2),
            "pe":round(pe,1),"fwd_pe":round(fwd_pe,1),"peg":round(peg,2),
            "eps":round(eps,2),"shares":round(shares/1e8,2)
        }
    except Exception as e:
        return None

def layer1_run(candidates):
    """运行Layer 1: 基本面筛选"""
    print(f"\n{'='*80}")
    print(f"  Layer 1: 基本面筛选")
    print(f"  候选池: {len(candidates)}只 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*80}")
    
    results = []
    for code,name,desc,rarity in candidates:
        data = layer1_financial_filter(code)
        if data:
            data["name"]=name;data["desc"]=desc;data["rarity"]=rarity
            results.append(data)
            print(f"  {name}({code}): PE={data['pe']:.0f}x OCF/NP={data['ocf_np']:.2f} 增长={data['np_g']:+.0f}%")
        else:
            print(f"  {name}({code}): 数据获取失败")
        time.sleep(0.5)  # 防限流
    
    # 打分
    for r in results:
        ocf_score = 3 if r["ocf_np"]>1.2 else (2 if r["ocf_np"]>0.8 else (1 if r["ocf_np"]>0.5 else 0))
        peg_score = 3 if r["peg"]<0.8 else (2 if r["peg"]<1.5 else (1 if r["peg"]<3.0 else 0))
        growth_score = 3 if r["np_g"]>50 else (2 if r["np_g"]>20 else (1 if r["np_g"]>0 else 0))
        rarity_score = r["rarity"]  # 1-5
        
        r["ocf_score"]=ocf_score;r["peg_score"]=peg_score
        r["growth_score"]=growth_score;r["rarity_score"]=rarity_score
        r["total_score"] = round(ocf_score*0.30 + peg_score*0.25 + growth_score*0.25 + rarity_score*0.20, 2)
        
        # 通过与否
        passes = ocf_score>=2 and peg_score>=2 and growth_score>=2
        r["pass_layer1"] = passes
    
    # 排序输出
    results.sort(key=lambda x:x["total_score"], reverse=True)
    
    print(f"\n{'='*100}")
    print(f"{'排名':<4} {'公司':<10} {'OCF分':<6} {'PEG分':<6} {'增长分':<6} {'稀缺分':<6} {'总分':<6} {'OCF/NP':<8} {'PEG':<8} {'增长':<8} {'PE':<8} {'通过'}")
    print(f"{'─'*100}")
    
    passed=[]
    for i,r in enumerate(results,1):
        p = "✅" if r["pass_layer1"] else "❌"
        if r["pass_layer1"]: passed.append(r)
        print(f"{i:<4} {r['name']:<10} {r['ocf_score']:<6} {r['peg_score']:<6} {r['growth_score']:<6} {r['rarity_score']:<6} {r['total_score']:<6.2f} {r['ocf_np']:<8.2f} {r['peg']:<8.2f} {r['np_g']:<+7.1f}% {r['pe']:<7.1f}x {p}")
    
    print(f"\n{'─'*100}")
    print(f"  通过Layer 1: {len(passed)}/{len(results)}")
    print(f"  条件: OCF/NP>0.8 + PEG<1.5 + 增长>20%")
    print(f"{'─'*100}")
    
    with open(OUT/"layer1_pool.json","w",encoding="utf-8") as f:
        json.dump({"date":str(datetime.now()),"passed":passed,"total":len(results)},f,ensure_ascii=False,indent=2)
    print(f"  保存至: {OUT}/layer1_pool.json")
    
    return passed, results

# ===================== Layer 2: V4时机判断 =====================
def zscore(s,w=20):
    r=s.rolling(w,min_periods=w);mu=r.mean();sd=r.std().replace(0,np.nan);return (s-mu)/sd

def v4_factors(d):
    f1=_i1(d);f2=_i2(d);f3=_i3(d);f4=_i4(d);f5=_i5(d)
    m=f1.merge(f2,on="date").merge(f3,on="date").merge(f4,on="date").merge(f5,on="date")
    for c in ["ir","tr","lr","br","nr"]:m[c+"_n"]=zscore(m[c],20)
    w={"ir":0.25,"tr":0.20,"lr":0.20,"br":0.20,"nr":0.15}
    m["rs"]=sum(w[k]*m[k+"_n"].fillna(0) for k in w);m["rz"]=zscore(m["rs"],20)
    m["sig"]=0;m.loc[m["rz"]>1.5,"sig"]=1;m.loc[m["rz"]<-1.5,"sig"]=-1
    return m

def _i1(dd):dd=dd.copy();dd["r20"]=dd["close"].pct_change(20);dd["ps"]=zscore(dd["r20"],20);dd["a5"]=dd["amount"].rolling(5).mean();dd["ar"]=dd["amount"]/dd["a5"].replace(0,np.nan);dd["ifl"]=dd["pct_chg"]*dd["ar"];dd["ifs"]=dd["ifl"].rolling(5).mean();dd["tz"]=zscore(dd["turnover"]);av2=(dd["high"]-dd["low"])/dd["close"].shift(1);dd["az"]=zscore(av2);dd["ls"]=((dd["tz"]>2)&(dd["az"]>2)).astype(int);dd["ir"]=(dd["ps"].fillna(0)*0.35+dd["ifs"].fillna(0)*0.40+dd["ls"].fillna(0)*0.25).rolling(5).mean().fillna(0);return dd[["date","ir"]]
def _i2(dd):dd=dd.copy();dd["rs"]=dd["close"].pct_change(5);dd["rm"]=dd["close"].pct_change(20);dd["rl"]=dd["close"].pct_change(60);dd["ms"]=zscore(2*dd["rs"].fillna(0)-dd["rm"].fillna(0)-dd["rl"].fillna(0));dr=dd["close"].pct_change();vs=dr.rolling(5).std();vl=dr.rolling(20).std();dd["vt"]=zscore(vs/vl.replace(0,np.nan)-1);dd["or_"]=dd["open"]/dd["close"].shift(1)-1;dd["or"]=np.where(dd["pct_chg"].abs()>0.001,dd["or_"]/dd["pct_chg"].replace(0,np.nan),0);dd["ors"]=zscore(dd["or"].rolling(10).mean());dd["tr"]=(dd["ms"].fillna(0)*0.35+dd["vt"].fillna(0)*0.30+dd["ors"].fillna(0)*0.35).rolling(5).mean().fillna(0);return dd[["date","tr"]]
def _i3(dd):dd=dd.copy();dd["am_"]=(dd["pct_chg"].abs()/(dd["amount"]/1e8)).replace([np.inf,-np.inf],np.nan);dd["af"]=zscore(dd["am_"].rolling(10).mean());dd["t20"]=dd["turnover"].rolling(20).mean();dd["ts20"]=dd["turnover"].rolling(20).std().replace(0,np.nan);dd["tzs"]=(dd["turnover"]-dd["t20"])/dd["ts20"];dd["tf"]=-zscore(dd["tzs"]);av3=(dd["high"]-dd["low"])/dd["close"].shift(1);dd["pi"]=(av3/(dd["turnover"]+0.01)).replace([np.inf,-np.inf],np.nan);dd["ipf"]=zscore(dd["pi"].rolling(10).mean());dd["lr"]=(dd["af"].fillna(0)*0.40+dd["tf"].fillna(0)*0.35+dd["ipf"].fillna(0)*0.25).rolling(5).mean().fillna(0);return dd[["date","lr"]]
def _i4(dd):dd=dd.copy();dd["ret"]=dd["close"].pct_change();dd["r5"]=dd["close"].pct_change(5);dd["rv"]=-zscore(dd["r5"]);pchg=dd["pct_chg"].fillna(0);thr=pchg.rolling(60).quantile(0.90);dd["eu"]=(pchg>thr.fillna(2)).astype(int);dd["lb"]=(dd["ret"].rolling(3).mean()*dd["eu"].shift(1)).rolling(3).mean();dd["lf"]=zscore(dd["lb"]);cr=dd["close"].pct_change(20).fillna(0);dd["itm"]=(cr>0.05).astype(float);dd["il"]=(cr<-0.05).astype(float);dd["dp"]=(dd["itm"]*(-dd["r5"].fillna(0))+dd["il"]*dd["r5"].fillna(0)).rolling(5).mean();dd["dpf"]=zscore(dd["dp"]);dd["br"]=(dd["rv"].fillna(0)*0.35+dd["lf"].fillna(0)*0.30+dd["dpf"].fillna(0)*0.35).rolling(5).mean().fillna(0);return dd[["date","br"]]
def _i5(dd):dd=dd.copy();pchg=dd["pct_chg"].fillna(0);thr=pchg.rolling(60).quantile(0.90);dd["eu"]=(pchg>thr.fillna(2)).astype(float);dd["tz"]=zscore(dd["turnover"]);lc=np.where(dd["eu"]==1,-dd["tz"].fillna(0),0);dd["lc"]=zscore(pd.Series(lc).rolling(3).mean());dd5=dd["close"].rolling(5).min()/dd["close"].rolling(5).max()-1;nf=np.where(dd5.fillna(0)<-0.05,-dd5.fillna(0),0);dd["nf"]=zscore(pd.Series(nf));dd["mp"]=(dd["pct_chg"]*dd["amount"]/dd["amount"].rolling(20).mean()).rolling(5).mean();dd["mf"]=zscore(dd["mp"]);dd["nr"]=(dd["lc"].fillna(0)*0.35+dd["nf"].fillna(0)*0.25+dd["mf"].fillna(0)*0.40).rolling(5).mean().fillna(0);return dd[["date","nr"]]

def layer2_v4_signal(code):
    """获取单只股票的V4信号"""
    try:
        exch="sh" if str(code).startswith("6") else "sz"
        df=ak.stock_zh_a_daily(symbol=exch+str(code),start_date="20240101",end_date="20260625",adjust="qfq")
        d=df.copy().sort_values("date").reset_index(drop=True);d["pct_chg"]=d["close"].pct_change()*100
        m=v4_factors(d)
        last=m.iloc[-1];si=int(last["sig"])
        st={1:"BUY",-1:"SELL",0:"HOLD"}[si]
        fv={k:round(float(last.get(k+"_n",0)),3) for k in ["ir","tr","lr","br","nr"]}
        return {
            "signal":si,"signal_text":st,"zscore":round(float(last["rz"]),3),
            "factors":fv,"price":round(float(d["close"].iloc[-1]),2)
        }
    except:
        return None

def layer2_run(stock_list):
    """运行Layer 2: V4时机判断"""
    print(f"\n{'='*80}")
    print(f"  Layer 2: V4时机判断")
    print(f"  分析对象: {len(stock_list)}只（通过Layer 1的标的）")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*80}")
    
    results = []
    for r in stock_list:
        v4 = layer2_v4_signal(r["code"])
        if v4:
            r.update(v4)
            results.append(r)
            icon = "🟢" if v4["signal_text"]=="BUY" else ("🔴" if v4["signal_text"]=="SELL" else "⚪")
            print(f"  {icon} {r['name']}({r['code']}): {v4['signal_text']} z={v4['zscore']:+0.3f}")
        time.sleep(0.3)
    
    # 操作建议
    print(f"\n{'='*80}")
    print(f"  综合操作建议（Layer 1通过 + Layer 2信号）")
    print(f"{'='*80}")
    print(f"{'信号':<6} {'公司':<10} {'代码':<8} {'zscore':<8} {'Layer1总分':<10} {'建议操作':<20} {'说明'}")
    print(f"{'─'*80}")
    
    for r in sorted(results, key=lambda x:x.get("zscore",-99), reverse=True):
        sig=r["signal_text"]
        z=r["zscore"]
        ts=r["total_score"]
        
        if sig=="BUY": action="🟢 建仓/加仓"; note="Layer1+Layer2双确认"
        elif sig=="SELL": action="🔴 减仓/清仓"; note="Layer1确认但V4触发出清"
        elif z>0.5: action="⬆ 持有(偏多)"; note="Layer1通过,V4偏多"
        elif z>-0.5: action="⚪ 持有(观望)"; note="Layer1通过,V4中性"
        else: action="⬇ 持有(警惕)"; note="Layer1通过但V4走弱"
        
        print(f"{sig:<6} {r['name']:<10} {str(r['code']):<8} {z:<+8.3f} {ts:<10.2f} {action:<20} {note}")
    
    print(f"{'─'*80}")
    
    with open(OUT/"layer2_signals.json","w",encoding="utf-8") as f:
        json.dump({"date":str(datetime.now()),"signals":results},f,ensure_ascii=False,indent=2)
    print(f"  保存至: {OUT}/layer2_signals.json")
    
    return results

# ===================== 合并报告 =====================
def full_report(passed, all_layer1, layer2_results):
    """生成完整合并报告"""
    print(f"\n{'='*95}")
    print(f"  亚翔集成分层选股模型 — 完整报告")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')} | 候选池{len(CANDIDATES)}只 → 通过Layer1 {len(passed)}只 → Layer2完成")
    print(f"{'='*95}")
    print(f"{'信号':<6} {'排名':<4} {'公司':<10} {'代码':<8} {'zscore':<8} {'OCF/NP':<8} {'PEG':<8} {'增长':<8} {'PE':<8} {'操作'}")
    print(f"{'─'*95}")
    
    l2 = {r["code"]:r for r in layer2_results}
    
    # 按V4信号排序: BUY > 偏多HOLD > 中性HOLD > 偏弱HOLD > SELL
    def sort_key(r):
        sig=r.get("signal",0)
        z=r.get("zscore",0)
        return (-sig if sig!=0 else 0, -z if z else 0)
    
    combined = sorted(l2.values(), key=sort_key)
    
    for i,r in enumerate(combined,1):
        sig=r.get("signal_text","?")
        z=r.get("zscore",0)
        ocf=r.get("ocf_np",0)
        peg_v=r.get("peg",0)
        ng=r.get("np_g",0)
        pe_v=r.get("pe",0)
        
        if sig=="BUY": action="🟢 建仓"; rank_icon="★"
        elif sig=="SELL": action="🔴 减仓"; rank_icon=""
        elif z>0.5: action="⬆ 持有(偏多)"; rank_icon=""
        else: action="⚪ 持有(观望)"; rank_icon=""
        
        print(f"{sig:<6} {rank_icon+' '+str(i) if rank_icon else str(i):<4} {r['name']:<10} {str(r['code']):<8} {z:<+8.3f} {ocf:<8.2f} {peg_v:<8.2f} {ng:<+7.1f}% {pe_v:<7.1f}x {action}")
    
    print(f"{'─'*95}")
    print(f"  买入池: {len([r for r in combined if r.get('signal')==1])}只")
    print(f"  持有池: {len([r for r in combined if r.get('signal')==0])}只")  
    print(f"  减仓池: {len([r for r in combined if r.get('signal')==-1])}只")
    print(f"{'─'*95}")
    
    rep = {
        "date":str(datetime.now()),"total_candidates":len(CANDIDATES),
        "layer1_passed":len(passed),"layer1_failed":len(all_layer1)-len(passed),
        "layer2_completed":len(combined),
        "summary":{
            "buy":len([r for r in combined if r.get("signal")==1]),
            "hold":len([r for r in combined if r.get("signal")==0]),
            "sell":len([r for r in combined if r.get("signal")==-1]),
        },
        "recommendations":combined
    }
    with open(OUT/"full_report.json","w",encoding="utf-8") as f:
        json.dump(rep,f,ensure_ascii=False,indent=2)
    print(f"\n  完整报告保存至: {OUT}/full_report.json")
    print(f"{'='*95}")
    
    return rep

# ===================== 主入口 =====================
if __name__ == "__main__":
    print(f"\n{'='*80}")
    print(f"  亚翔集成分层选股模型 v1.0")
    print(f"  Layer 1: 基本面筛选 | Layer 2: V4时机判断")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*80}")
    
    # === Layer 1: 基本面筛选 ===
    passed, all_layer1 = layer1_run(CANDIDATES)
    
    # === Layer 2: V4时机判断（仅对通过Layer1的标的运行） ===
    if passed:
        layer2_results = layer2_run(passed)
        # === 完整报告 ===
        full_report(passed, all_layer1, layer2_results)
    else:
        print("\n  Layer 1 无通过标的，Layer 2 跳过")
    
    print(f"\n  运行完成 ✅")
