import requests
import time
from datetime import datetime, timedelta

# ============ 你的 Key 硬编码（仓库必须 Private！）============
AV_KEY = "RJOD99KWLLHMWZ1X"
SC_KEY = "SCT304469THjZDZYoN5gi8OObrh2lkfOEc"
# ====================================================================

# 北京时间
beijing_time = datetime.utcnow() + timedelta(hours=8)
date_str = beijing_time.strftime('%Y-%m-%d %H:%M')

# 只保留7大美股（Alpha Vantage 完美支持）
tickers = {
    "英伟达": "NVDA",
    "特斯拉": "TSLA",
    "苹果": "AAPL",
    "谷歌": "GOOGL",
    "Meta": "META",
    "微软": "MSFT",
    "亚马逊": "AMZN"
}

results = []

for i, (name, symbol) in enumerate(tickers.items()):
    if i > 0:
        time.sleep(15)  # 防限流，稳的一批

    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "RSI",
            "symbol": symbol,
            "interval": "daily",
            "time_period": 14,
            "series_type": "close",
            "apikey": AV_KEY
        }
        r = requests.get(url, params=params, timeout=20)
        data = r.json()

        if "Note" in data or "Information" in data:
            error_msg = data.get("Note") or data.get("Information", "")
            if "rate limit" in error_msg.lower():
                rsi_text = "限流了（明天再来）"
                rsi_value = None
            else:
                rsi_text = "API错误"
                rsi_value = None
        elif "Technical Analysis: RSI" not in data:
            rsi_text = "无数据"
            rsi_value = None
        else:
            latest_date = max(data["Technical Analysis: RSI"].keys())
            rsi = float(data["Technical Analysis: RSI"][latest_date]["RSI"])
            rsi_value = rsi
            if rsi > 70:
                rsi_text = f"🔥 {rsi:.2f} ↑超买"
            elif rsi < 30:
                rsi_text = f"❄️ {rsi:.2f} ↓超卖"
            else:
                rsi_text = f"{rsi:.2f}"
        
        results.append({"name": name, "symbol": symbol, "rsi": rsi_value, "rsi_text": rsi_text})

    except Exception as e:
        results.append({"name": name, "symbol": symbol, "rsi": None, "rsi_text": "请求异常"})

# 按 RSI 从低到高排序（无数据放最下面）
results.sort(key=lambda x: (x["rsi"] is None, x["rsi"]))

# 构建消息
message = f"### 每日RSI排行（由低→高）\n\n"
message += f"**日线14期RSI**（更新：{date_str} 北京时间）\n\n"
message += "| 标的   | 代码     | RSI         |\n"
message += "|--------|----------|-------------|\n"

for item in results:
    message += f"| {item['name']:<4} | {item['symbol']:<6} | {item['rsi_text']} |\n"

# Server酱推送
title = f"每日RSI排行 {beijing_time.strftime('%Y-%m-%d')}"
push_url = f"https://sctapi.ftqq.com/{SC_KEY}.send"
requests.post(push_url, data={"title": title, "desp": message})