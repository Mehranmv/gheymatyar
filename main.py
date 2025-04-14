import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper function to fetch price
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


async def crypto_price(endpoint):
    url = f"https://api.nobitex.ir/market/stats?srcCurrency={endpoint}&dstCurrency=rls"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json().get("stats").get(f"{endpoint}-rls").get("latest")


@app.get("/api/crypto")
async def get_crypto():
    return {
        "btc": await crypto_price("btc"),
        "usdt": await crypto_price("usdt"),
        "eth": await crypto_price("eth"),
    }


@app.get("/api/prices")
async def get_prices():
    return {
        "usd": await fetch_price("usd"),
        "gold": await fetch_price("gold-miskal"),
        "coin": await fetch_price("coin-baharazadi"),
    }


# Serve static index.html
@app.get("/")
def serve_index():
    return FileResponse("static/index.html")


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
