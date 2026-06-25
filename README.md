# 亚翔集成分层选股模型 v1.0

## 模型架构
- Layer 1: 基本面筛选（OCF/NP>0.8 + PEG<1.5 + 增长>20% + 稀缺性）
- Layer 2: V4时机判断（五租金因子择时）
- 两个Layer完全独立数据源，避免双重计入

## 本地运行
```bash
pip install -r requirements.txt
python model_layer1.py
```
输出文件在 outputs/ 目录下

## GitHub Actions 云端部署

### 方法一: 一键部署（推荐）
1. 在 GitHub 创建新仓库
2. 把 outputs/ 目录下的所有文件上传到仓库根目录
3. GitHub Actions 会自动在每天 15:30 运行
4. 在 Actions 页面查看运行结果

### 方法二: Fork 此仓库
直接 Fork，Workflow 自动生效

## 输出文件说明
- full_report.json — 完整合并报告
- layer1_pool.json — 基本面筛选通过名单
- layer2_signals.json — V4时机信号
