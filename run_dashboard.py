import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("LAUNCHING E-COMMERCE MEDALLION LAKEHOUSE DASHBOARD")
    print("Local URL: http://localhost:8000")
    print("=" * 60)
    
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
