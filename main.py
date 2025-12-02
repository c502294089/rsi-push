import requests
import datetime
import yfinance as yf

# ====== 你的 SendKey（来自 Server酱）======
SENDKEY = "SCT304469THjZDZYoN5gi8OObrh2lkfOEc"

# ====== 关注的标的 ======
symbols = {
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",
    "Apple": "AAPL",
    "Google": "GOOGL",
    "Meta": "META",
    "Microsoft": "MSFT",
    "Amazon": "AMZN",
    "NASDAQ指数": "^IXIC",
    "黄金": "GC=F",
    "比特币": "BTC-USD"
}

# ====== RSI 计算函数 ======
def compute_rsi(prices, period=14):
    delta = prices.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    avg_up = up.rolling(window=period).mean()
    avg_down = down.rolling(window=period).mean()
    rs = avg_up / avg_down
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ====== 获取 RSI ======
def get_rsi(symbol):
    data = yf.download(symbol, period="3mo", interval="1d")
    if len(data) < 15:
        return None
    rsi = compute_rsi(data["Close"])
    return round(rsi[-1], 2)

# ====== 生成推送内容 ======
def build_message():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    msg = f"📊 今日 RSI（{today}）\n\n"
    for name, ticker in symbols.items():
        rsi = get_rsi(ticker)
        msg += f"{name} ({ticker}) → RSI: {rsi}\n"
    return msg

# ====== Server酱推送 ======
def send_wechat(msg):
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = {
        "title": "今日股票 & 加密 RSI 指标",
        "desp": msg
    }
    requests.post(url, data=data)

# ====== 执行 ======
if __name__ == "__main__":
    message = build_message()
    send_wechat(message)
    print("已推送到微信！")
