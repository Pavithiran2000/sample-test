# CPD-3-AI

A FastAPI backend service that uses AI to parse natural language payment instructions into structured payment schedules for real estate companies.

## ✨ Features

- **🔐 JWT Authentication**: Secure token-based authentication with RS256
- **🤖 AI-Powered Parsing**: Google Gemini integration for natural language processing
- **� Smart Payment Calculations**: Equal divisions, percentage-based payments, custom schedules
- **📊 Flexible Input**: Supports various prompt formats and amount specifications
- **🌐 REST API**: Clean, documented FastAPI endpoints
- **🔧 CORS Support**: Cross-origin requests enabled for frontend integration
- **✅ Input Validation**: Comprehensive validation and error handling


## 🛠️ Setup & Installation

1. **Clone and navigate to the project**
   ```bash
   cd cpd-3-ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create/update `.env` file:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ACCESS_TOKEN_PUBLIC_KEY=your_access_token_public_key_here
   REFRESH_TOKEN_PUBLIC_KEY=your_refresh_token_public_key_here
   LLM_PROVIDER=gemini
   HOST=127.0.0.1
   PORT=5000
   ```

5. **Run the application**
   ```bash
   # Using new structured version
   python main.py
   
   # Or using uvicorn directly
   uvicorn main:app --host 127.0.0.1 --port 5000 --reload
   ```

## 📋 API Endpoints

### Health & Status
- `GET /health` - Service health check
- `GET /auth-status` - Authentication status check

### Payment Schedule
- `POST /parse-payment-schedule` - Parse payment schedule from prompt (requires auth)

##  Production Deployment

For production deployment:

1. **Set environment variables properly**
2. **Use production ASGI server** (e.g., Gunicorn + Uvicorn)
3. **Configure reverse proxy** (Nginx)
4. **Enable HTTPS**
5. **Set up monitoring and logging**

##  Contributing

1. Follow the established folder structure
2. Add tests for new features
3. Update documentation
4. Follow Python coding standards (PEP 8)

##  License

This project is part of CPD-3-AI integration system.
