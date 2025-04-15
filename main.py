import time
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# نرخ لحظه‌ای
async def fetch_price(endpoint: str) -> int:
    url = f"https://api.priceto.day/v1/latest/irr/{endpoint}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json().get("price")
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"خطا در دریافت قیمت {endpoint}: {str(e)}"
        )


async def crypto_price(endpoint: str) -> int:
    url = f"https://api.nobitex.ir/market/stats?srcCurrency={endpoint}&dstCurrency=rls"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()["stats"][f"{endpoint}-rls"]["latest"]


@app.get("/api/prices")
async def get_prices():
    return {
        "usd": await fetch_price("usd"),
        "gold": await fetch_price("gold-miskal"),
        "coin": await fetch_price("coin-baharazadi"),
    }


@app.get("/api/crypto")
async def get_crypto():
    return {
        "btc": await crypto_price("btc"),
        "usdt": await crypto_price("usdt"),
        "eth": await crypto_price("eth"),
    }


# تاریخچه برای ارزهای سنتی
@app.get("/api/history/local/{type}")
async def get_local_history(
    type: str,
    from_date: str = Query(..., description="مثلاً 2024-01-01"),
    to_date: str = Query(..., description="مثلاً 2024-02-01"),
):
    url = f"https://api.priceto.day/v1/history/irr/{type}?from={from_date}T00:00:00z&to={to_date}T00:00:00z"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()["result"]
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"خطا در دریافت تاریخچه: {str(e)}")


# تاریخچه رمز ارزها
@app.get("/api/history/crypto/{symbol}")
async def get_crypto_history(
    symbol: str,
    from_ts: datetime,
    to_ts: datetime,
    resolution: str = "60",
):
    market = symbol.upper() + "IRT"
    from_ts = datetime.timestamp(from_ts)
    to_ts = datetime.timestamp(to_ts)
    print(from_ts, to_ts)
    # url = f"https://api.nobitex.ir/market/udf/history?symbol={market}&resolution={resolution}&from={from_ts}&to={to_ts}"
    url = f"https://api.nobitex.ir/market/udf/history?symbol={market}&resolution={resolution}&from=1562058167&to=1562230967"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"خطا در دریافت تاریخچه رمز ارز: {str(e)}"
        )


# Serve static HTML
@app.get("/")
def serve_index():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
