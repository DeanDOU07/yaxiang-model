#!/usr/bin/env python3
"""
浜氱繑闆嗘垚鍒嗗眰閫夎偂妯″瀷 v1.0
============================
Layer 1: 鍩烘湰闈㈢瓫閫夛紙浣庨, 瀛ｆ姤鏇存柊锛?Layer 2: V4鏃舵満鍒ゆ柇锛堥珮棰? 鏃ラ鏇存柊锛?
浣滆€? Codex
鏃ユ湡: 2026-06-25
"""

import akshare as ak
import pandas as pd
import numpy as np
import json, sys, io, time
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ===================== 閰嶇疆鍖?=====================
OUT = Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)

# 鍊欓€夎偂绁ㄦ睜锛堝彲鑷澧炲垹锛?CANDIDATES = [
    # (浠ｇ爜, 鍚嶇О, 缁嗗垎棰嗗煙, 绋€缂烘€ц瘎鍒?-5)
    ("300308","涓檯鏃垱","鍏夋ā鍧?鍏ㄧ悆绗竴)",5),
    ("601138","宸ヤ笟瀵岃仈","AI鏈嶅姟鍣ㄤ唬宸?,5),
    ("603929","浜氱繑闆嗘垚","娲佸噣瀹?鍞竴)",5),
    ("002916","娣卞崡鐢佃矾","IC灏佽鍩烘澘(鍞竴)",5),
    ("002281","鍏夎繀绉戞妧","鍏夎姱鐗?鑷爺EML)",4),
    ("002837","鑻辩淮鍏?,"AI娑插喎CDU",4),
    ("002851","楹︽牸绫崇壒","AI鐢垫簮(鑻变紵杈鹃摼)",5),
    ("002409","闆呭厠绉戞妧","HBM鍓嶉┍浣?,4),
    ("600584","闀跨數绉戞妧","鍏堣繘灏佽(CoWoS)",4),
    ("600183","鐢熺泭绉戞妧","楂橀瑕嗛摐鏉?鍥藉唴绗竴)",4),
    ("603986","鍏嗘槗鍒涙柊","NOR Flash+MCU",4),
    ("300476","鑳滃畯绉戞妧","AI鏈嶅姟鍣≒CB",3),
    ("300274","闃冲厜鐢垫簮","閫嗗彉鍣?鍏ㄧ悆绗竴)",5),
    ("300474","鏅槈寰?,"GPU(鍞竴)",5),
    ("301269","鍗庡ぇ涔濆ぉ","EDA(鍞竴)",5),
    ("688981","涓姱鍥介檯","鏅跺渾浠ｅ伐(鍞竴)",5),
    ("002475","绔嬭绮惧瘑","杩炴帴鍣ㄩ緳澶?,3),
    ("300124","姹囧窛鎶€鏈?,"宸ユ帶AI浼烘湇",4),
    ("688012","涓井鍏徃","鍒昏殌璁惧(鍞竴)",5),
    ("002371","鍖楁柟鍗庡垱","鍗婂浣撹澶囧钩鍙?,4),
    ("688008","婢滆捣绉戞妧","DDR5鎺ュ彛(鍞竴)",5),
    ("688256","瀵掓绾?,"AI鑺墖(鍞竴)",5),
    ("300502","鏂版槗鐩?,"800G鍏夋ā鍧?,4),
    ("002156","閫氬瘜寰數","鍏堣繘灏佽(AMD閾?",4),
    ("002436","鍏存．绉戞妧","FCBGA灏佽鍩烘澘",4),
    ("300394","澶╁瓪閫氫俊","鍏夊紩鎿?,4),
    ("688041","娴峰厜淇℃伅","CPU+DCU(鍞竴)",5),
    ("688268","鍗庣壒姘斾綋","鐢靛瓙鐗规皵",3),
    ("688234","澶╁渤鍏堣繘","SiC琛簳",4),
    ("002428","浜戝崡閿椾笟","纾峰寲閾烮nP琛簳",4),
    ("300346","鍗楀ぇ鍏夌數","MO婧?鍏夊埢鑳?,4),
    ("688629","鍗庝赴绉戞妧","楂橀€熻儗鏉胯繛鎺ュ櫒",4),
    ("688668","榧庨€氱鎶€","I/O杩炴帴鍣?,3),
    ("603738","娉版櫠绉戞妧","鏅朵綋鎸崱鍣?,3),
    ("300661","鍦ｉ偊鑲′唤","鐢垫簮绠＄悊IC",3),
]

# ===================== Layer 1: 鍩烘湰闈㈢瓫閫?=====================
def layer1_financial_filter(code):
    """鑾峰彇鍗曞彧鑲＄エ鐨勫熀鏈潰鎸囨爣"""
    try:
        fin = ak.stock_financial_abstract(symbol=str(code))
        def gm(n,c):
            r=fin[fin["鎸囨爣"]==n]
            if len(r)>0 and c in r.columns:v=r.iloc[0][c];return float(v) if pd.notna(v) else 0
            return 0
        
        np_y=gm("褰掓瘝鍑€鍒╂鼎","20251231")/1e8
        np_q1=gm("褰掓瘝鍑€鍒╂鼎","20260331")/1e8
        np_q1_25=gm("褰掓瘝鍑€鍒╂鼎","20250331")/1e8
        np_py=gm("褰掓瘝鍑€鍒╂鼎","20241231")/1e8
        ocf=gm("缁忚惀鐜伴噾娴侀噺鍑€棰?,"20251231")/1e8
        eps=gm("鍩烘湰姣忚偂鏀剁泭","20251231")
        rev_y=gm("钀ヤ笟鎬绘敹鍏?,"20251231")/1e8
        
        # 鍑€鍒╁闀?        np_g=(np_y/np_py-1)*100 if np_py>0 else 0
        # 鎬昏偂鏈?        shares=np_y*1e8/eps if eps>0 else 0
        
        # 鑾峰彇褰撳墠浠锋牸
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
    """杩愯Layer 1: 鍩烘湰闈㈢瓫閫?""
    print(f"\n{'='*80}")
    print(f"  Layer 1: 鍩烘湰闈㈢瓫閫?)
    print(f"  鍊欓€夋睜: {len(candidates)}鍙?| {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*80}")
    
    results = []
    for code,name,desc,rarity in candidates:
        data = layer1_financial_filter(code)
        if data:
            data["name"]=name;data["desc"]=desc;data["rarity"]=rarity
            results.append(data)
            print(f"  {name}({code}): PE={data['pe']:.0f}x OCF/NP={data['ocf_np']:.2f} 澧為暱={data['np_g']:+.0f}%")
        else:
            print(f"  {name}({code}): 鏁版嵁鑾峰彇澶辫触")
        time.sleep(0.5)  # 闃查檺娴?    
    # 鎵撳垎
    for r in results:
        ocf_score = 3 if r["ocf_np"]>1.2 else (2 if r["ocf_np"]>0.8 else (1 if r["ocf_np"]>0.5 else 0))
        peg_score = 3 if r["peg"]<0.8 else (2 if r["peg"]<1.5 else (1 if r["peg"]<3.0 else 0))
        growth_score = 3 if r["np_g"]>50 else (2 if r["np_g"]>20 else (1 if r["np_g"]>0 else 0))
        rarity_score = r["rarity"]  # 1-5
        
        r["ocf_score"]=ocf_score;r["peg_score"]=peg_score
        r["growth_score"]=growth_score;r["rarity_score"]=rarity_score
        r["total_score"] = round(ocf_score*0.30 + peg_score*0.25 + growth_score*0.25 + rarity_score*0.20, 2)
        
        # 閫氳繃涓庡惁
        passes = ocf_score>=2 and peg_score>=2 and growth_score>=2
        r["pass_layer1"] = passes
    
    # 鎺掑簭杈撳嚭
    results.sort(key=lambda x:x["total_score"], reverse=True)
    
    print(f"\n{'='*100}")
    print(f"{'鎺掑悕':<4} {'鍏徃':<10} {'OCF鍒?:<6} {'PEG鍒?:<6} {'澧為暱鍒?:<6} {'绋€缂哄垎':<6} {'鎬诲垎':<6} {'OCF/NP':<8} {'PEG':<8} {'澧為暱':<8} {'PE':<8} {'閫氳繃'}")
    print(f"{'鈹€'*100}")
    
    passed=[]
    for i,r in enumerate(results,1):
        p = "鉁? if r["pass_layer1"] else "鉂?
        if r["pass_layer1"]: passed.append(r)
        print(f"{i:<4} {r['name']:<10} {r['ocf_score']:<6} {r['peg_score']:<6} {r['growth_score']:<6} {r['rarity_score']:<6} {r['total_score']:<6.2f} {r['ocf_np']:<8.2f} {r['peg']:<8.2f} {r['np_g']:<+7.1f}% {r['pe']:<7.1f}x {p}")
    
    print(f"\n{'鈹€'*100}")
    print(f"  閫氳繃Layer 1: {len(passed)}/{len(results)}")
    print(f"  鏉′欢: OCF/NP>0.8 + PEG<1.5 + 澧為暱>20%")
    print(f"{'鈹€'*100}")
    
    with open(OUT/"layer1_pool.json","w",encoding="utf-8") as f:
        json.dump({"date":str(datetime.now()),"passed":passed,"total":len(results)},f,ensure_ascii=False,indent=2)
    print(f"  淇濆瓨鑷? {OUT}/layer1_pool.json")
    
    return passed, results

# ===================== Layer 2: V4鏃舵満鍒ゆ柇 =====================
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
    """鑾峰彇鍗曞彧鑲＄エ鐨刅4淇″彿"""
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
    """杩愯Layer 2: V4鏃舵満鍒ゆ柇"""
    print(f"\n{'='*80}")
    print(f"  Layer 2: V4鏃舵満鍒ゆ柇")
    print(f"  鍒嗘瀽瀵硅薄: {len(stock_list)}鍙紙閫氳繃Layer 1鐨勬爣鐨勶級")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*80}")
    
    results = []
    for r in stock_list:
        v4 = layer2_v4_signal(r["code"])
        if v4:
            r.update(v4)
            results.append(r)
            icon = "馃煝" if v4["signal_text"]=="BUY" else ("馃敶" if v4["signal_text"]=="SELL" else "鈿?)
            print(f"  {icon} {r['name']}({r['code']}): {v4['signal_text']} z={v4['zscore']:+0.3f}")
        time.sleep(0.3)
    
    # 鎿嶄綔寤鸿
    print(f"\n{'='*80}")
    print(f"  缁煎悎鎿嶄綔寤鸿锛圠ayer 1閫氳繃 + Layer 2淇″彿锛?)
    print(f"{'='*80}")
    print(f"{'淇″彿':<6} {'鍏徃':<10} {'浠ｇ爜':<8} {'zscore':<8} {'Layer1鎬诲垎':<10} {'寤鸿鎿嶄綔':<20} {'璇存槑'}")
    print(f"{'鈹€'*80}")
    
    for r in sorted(results, key=lambda x:x.get("zscore",-99), reverse=True):
        sig=r["signal_text"]
        z=r["zscore"]
        ts=r["total_score"]
        
        if sig=="BUY": action="馃煝 寤轰粨/鍔犱粨"; note="Layer1+Layer2鍙岀‘璁?
        elif sig=="SELL": action="馃敶 鍑忎粨/娓呬粨"; note="Layer1纭浣哣4瑙﹀彂鍑烘竻"
        elif z>0.5: action="猬?鎸佹湁(鍋忓)"; note="Layer1閫氳繃,V4鍋忓"
        elif z>-0.5: action="鈿?鎸佹湁(瑙傛湜)"; note="Layer1閫氳繃,V4涓€?
        else: action="猬?鎸佹湁(璀︽儠)"; note="Layer1閫氳繃浣哣4璧板急"
        
        print(f"{sig:<6} {r['name']:<10} {str(r['code']):<8} {z:<+8.3f} {ts:<10.2f} {action:<20} {note}")
    
    print(f"{'鈹€'*80}")
    
    with open(OUT/"layer2_signals.json","w",encoding="utf-8") as f:
        json.dump({"date":str(datetime.now()),"signals":results},f,ensure_ascii=False,indent=2)
    print(f"  淇濆瓨鑷? {OUT}/layer2_signals.json")
    
    return results

# ===================== 鍚堝苟鎶ュ憡 =====================
def full_report(passed, all_layer1, layer2_results):
    """鐢熸垚瀹屾暣鍚堝苟鎶ュ憡"""
    print(f"\n{'='*95}")
    print(f"  浜氱繑闆嗘垚鍒嗗眰閫夎偂妯″瀷 鈥?瀹屾暣鎶ュ憡")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')} | 鍊欓€夋睜{len(CANDIDATES)}鍙?鈫?閫氳繃Layer1 {len(passed)}鍙?鈫?Layer2瀹屾垚")
    print(f"{'='*95}")
    print(f"{'淇″彿':<6} {'鎺掑悕':<4} {'鍏徃':<10} {'浠ｇ爜':<8} {'zscore':<8} {'OCF/NP':<8} {'PEG':<8} {'澧為暱':<8} {'PE':<8} {'鎿嶄綔'}")
    print(f"{'鈹€'*95}")
    
    l2 = {r["code"]:r for r in layer2_results}
    
    # 鎸塚4淇″彿鎺掑簭: BUY > 鍋忓HOLD > 涓€OLD > 鍋忓急HOLD > SELL
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
        
        if sig=="BUY": action="馃煝 寤轰粨"; rank_icon="鈽?
        elif sig=="SELL": action="馃敶 鍑忎粨"; rank_icon=""
        elif z>0.5: action="猬?鎸佹湁(鍋忓)"; rank_icon=""
        else: action="鈿?鎸佹湁(瑙傛湜)"; rank_icon=""
        
        print(f"{sig:<6} {rank_icon+' '+str(i) if rank_icon else str(i):<4} {r['name']:<10} {str(r['code']):<8} {z:<+8.3f} {ocf:<8.2f} {peg_v:<8.2f} {ng:<+7.1f}% {pe_v:<7.1f}x {action}")
    
    print(f"{'鈹€'*95}")
    print(f"  涔板叆姹? {len([r for r in combined if r.get('signal')==1])}鍙?)
    print(f"  鎸佹湁姹? {len([r for r in combined if r.get('signal')==0])}鍙?)  
    print(f"  鍑忎粨姹? {len([r for r in combined if r.get('signal')==-1])}鍙?)
    print(f"{'鈹€'*95}")
    
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
    print(f"\n  瀹屾暣鎶ュ憡淇濆瓨鑷? {OUT}/full_report.json")
    print(f"{'='*95}")
    
    return rep

# ===================== 涓诲叆鍙?=====================
if __name__ == "__main__":
    print(f"\n{'='*80}")
    print(f"  浜氱繑闆嗘垚鍒嗗眰閫夎偂妯″瀷 v1.0")
    print(f"  Layer 1: 鍩烘湰闈㈢瓫閫?| Layer 2: V4鏃舵満鍒ゆ柇")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*80}")
    
    # === Layer 1: 鍩烘湰闈㈢瓫閫?===
    passed, all_layer1 = layer1_run(CANDIDATES)
    
    # === Layer 2: V4鏃舵満鍒ゆ柇锛堜粎瀵归€氳繃Layer1鐨勬爣鐨勮繍琛岋級 ===
    if passed:
        layer2_results = layer2_run(passed)
        # === 瀹屾暣鎶ュ憡 ===
        full_report(passed, all_layer1, layer2_results)
    else:
        print("\n  Layer 1 鏃犻€氳繃鏍囩殑锛孡ayer 2 璺宠繃")
    
    print(f"\n  杩愯瀹屾垚 鉁?)
