# Interior Space Optimization Backend

## Setup

1. **Create Virtual Environment** (if not exists):
   ```powershell
   python -m venv venv
   ```

2. **Activate Virtual Environment**:
   ```powershell
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

## Running the Server

```powershell
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
Docs: `http://127.0.0.1:8000/docs`
