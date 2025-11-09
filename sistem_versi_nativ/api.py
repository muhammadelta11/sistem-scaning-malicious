# api.py (Refactored)
import asyncio
import hashlib
import json
import logging
import os
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import pandas as pd
import uvicorn
from cachetools import TTLCache
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, EmailStr

# Import your existing modules
import core_scanner
import data_manager
from config import MALICIOUS_KEYWORDS # Assuming config.py has this

# --- Configuration & Setup ---
load_dotenv() # Load environment variables from .env

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Constants & Global Variables ---
DATABASE_FILE = 'users.db' # Make sure this file exists
ADMIN_SERPAPI_KEY = os.getenv("SERPAPI_API_KEY") # Admin key for fallback
if not ADMIN_SERPAPI_KEY:
    logger.warning("ADMIN_SERPAPI_KEY not found in .env. API fallback might not work.")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_key_for_jwt_change_this") # CHANGE THIS IN .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day expiration

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Caching (remains the same)
scan_cache = TTLCache(maxsize=100, ttl=3600) # Cache 1 hour
domain_info_cache = TTLCache(maxsize=50, ttl=86400) # Cache 24 hours

# ML Model (will be loaded at startup)
model = None
label_mapping = None

# Thread pool for blocking tasks
executor = ThreadPoolExecutor(max_workers=5) # Adjust worker count as needed

# --- FastAPI App Initialization ---
app = FastAPI(
    title="SEO Poisoning Detection API",
    description="Multi-user API for detecting SEO Poisoning with enhanced features.",
    version="3.0", # Updated version
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Be more restrictive in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Utilities ---
def get_db():
    """Dependency to get DB connection"""
    # Tambahkan check_same_thread=False di sini
    conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row # Return rows as dict-like objects
    try:
        yield conn # Ini yields koneksi untuk request
    finally:
        conn.close() # Ini menutupnya setelah request selesai

def log_activity(username: str, organization: str, action: str, details: str = "", conn: sqlite3.Connection = None):
    """Logs user activity to the database."""
    should_close = False
    if conn is None:
        conn = sqlite3.connect(DATABASE_FILE)
        should_close = True
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO activity_log (username, organization_name, action, details) VALUES (?, ?, ?, ?)",
            (username, organization, action, details)
        )
        conn.commit()
        logger.info(f"Logged: User='{username}', Org='{organization}', Action='{action}', Details='{details}'")
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")
    finally:
        if should_close:
            conn.close()

# --- Authentication Utilities ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserInDB(BaseModel):
    username: str
    role: str
    organization_name: str
    user_api_key: Optional[str] = None
    hashed_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: sqlite3.Connection, username: str) -> Optional[UserInDB]:
    """Fetches user from DB"""
    c = db.cursor()
    c.execute("SELECT username, role, organization_name, user_api_key, password_hash FROM users WHERE username = ?", (username,))
    user_row = c.fetchone()
    if user_row:
        return UserInDB(
            username=user_row["username"],
            role=user_row["role"],
            organization_name=user_row["organization_name"],
            user_api_key=user_row["user_api_key"],
            hashed_password=user_row["password_hash"]
        )
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: sqlite3.Connection = Depends(get_db)) -> UserInDB:
    """Dependency to get current logged-in user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Dependency to ensure user is an admin"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# --- Pydantic Models (API Request/Response) ---
class ScanRequest(BaseModel):
    domain: str = Field(..., description="Target domain without http://", example="example.com")
    scan_type: str = Field("cepat", description="Scan type: 'cepat' or 'komprehensif'", example="komprehensif")
    enable_verification: bool = Field(True, description="Enable real-time verification")
    # enable_backlink: bool = Field(False, description="Enable backlink analysis (currently disabled in API)") # Keep disabled for now
    # max_pages: int = Field(50, description="Max pages for crawling (used in Komprehensif)") # Maybe pass this to core_scanner later

class ScanResultItem(BaseModel):
    url: str
    title: str
    snippet: str
    confidence: Optional[float] = None
    verification: Optional[Dict[str, Any]] = None
    deep_analysis: Optional[Dict[str, Any]] = None
    js_analysis: Optional[Dict[str, Any]] = None # Add field for JS analysis

class ScanCategory(BaseModel):
    name: str
    items: List[ScanResultItem]

class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: Optional[str] = None
    domain: str
    timestamp: datetime
    scan_duration_seconds: Optional[float] = None
    results: Optional[Dict[str, ScanCategory]] = None # Changed from 'categories' to 'results' for clarity
    domain_info: Optional[Dict[str, Any]] = None
    graph_analysis: Optional[Dict[str, Any]] = None # Add field for graph analysis

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = Field("user", example="user")
    organization_name: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    organization_name: str
    user_api_key: Optional[str] = None

    class Config:
        orm_mode = True # For compatibility with SQL fetching

class LogEntry(BaseModel):
    id: int
    timestamp: datetime
    username: Optional[str] = None
    organization_name: Optional[str] = None
    action: str
    details: Optional[str] = None

    class Config:
        orm_mode = True

# --- API Endpoints ---

@app.on_event("startup")
async def startup_event():
    """Load resources on application startup"""
    global model, label_mapping
    # Use data_manager to load resources
    model, label_mapping, _ = data_manager.load_resources() # Ignore ranking_data for now
    if model:
        logger.info("Model ML berhasil dimuat")
    else:
        logger.warning("Model ML tidak ditemukan atau gagal dimuat")
    # Ensure label_mapping exists
    if not label_mapping:
         label_mapping = {1: 'hack_judol', 2: 'pornografi', 3: 'hacked', 0: 'aman'} # Basic fallback
         logger.info("Using basic fallback label mapping.")

    logger.info("API SEO Poisoning Detection siap")

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: sqlite3.Connection = Depends(get_db)):
    """Login endpoint to get JWT token"""
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        log_activity(form_data.username, "N/A", "LOGIN_FAIL", "Invalid credentials", db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    log_activity(user.username, user.organization_name, "LOGIN_SUCCESS", "", db)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    """Get current logged-in user details"""
    # Create a dummy row object for orm_mode compatibility
    user_dict = current_user.dict()
    user_dict['id'] = 0 # ID is not stored in UserInDB, provide dummy
    return UserResponse.from_orm(type('obj', (object,), user_dict)())


async def run_scan_in_background(scan_id: str, request: ScanRequest, user: UserInDB):
    """Function to run the blocking scan process in the background/thread"""
    start_time = time.time()
    loop = asyncio.get_event_loop()
    scan_status = {"status": "processing", "results": None, "error": None}

    try:
        # Determine API keys
        primary_key = user.user_api_key if user.role == 'user' and user.user_api_key else ADMIN_SERPAPI_KEY
        fallback_key = ADMIN_SERPAPI_KEY

        if not primary_key:
             raise ValueError("Primary API Key is not available.")

        # Log scan start
        key_type_used = 'user_key' if primary_key == user.user_api_key and user.role == 'user' else 'admin_key'
        log_activity(user.username, user.organization_name, 'START_SCAN', f"domain: {request.domain}, type: {request.scan_type}, key: {key_type_used}")

        # Run the synchronous core_scanner function in the thread pool
        scan_results_data = await loop.run_in_executor(
            executor,
            core_scanner.perform_verified_scan, # Call the function from core_scanner
            request.domain,
            primary_key,
            fallback_key,
            request.scan_type,
            False, # enable_backlink is False
            model,
            label_mapping,
            request.enable_verification
        )

        scan_duration = time.time() - start_time
        logger.info(f"Scan {scan_id} for {request.domain} completed in {scan_duration:.2f}s")

        # Process results for response (handle potential errors/empty results)
        if isinstance(scan_results_data, dict) and 'categories' in scan_results_data:
             # Convert category keys if necessary and structure for ScanResponse
             processed_categories = {}
             for cat_id, cat_data in scan_results_data.get('categories', {}).items():
                 # Ensure items are correctly formatted ScanResultItem if needed
                 processed_categories[str(cat_data.get("name", cat_id))] = ScanCategory(
                     name=cat_data.get("name", "Unknown"),
                     items=[ScanResultItem(**item) for item in cat_data.get("items", [])]
                 )

             # TODO: Persist the full results associated with scan_id in a database
             # For now, store in cache with processed structure
             final_response = ScanResponse(
                 scan_id=scan_id,
                 status="completed",
                 domain=request.domain,
                 timestamp=datetime.now(),
                 scan_duration_seconds=round(scan_duration, 2),
                 results=processed_categories,
                 domain_info=scan_results_data.get('domain_info'),
                 graph_analysis=scan_results_data.get('graph_analysis')
             )
             scan_cache[scan_id] = final_response # Cache by scan_id
             scan_status["status"] = "completed"
             scan_status["results"] = final_response

        elif isinstance(scan_results_data, dict) and scan_results_data.get("status") == "clean":
             logger.info(f"Scan {scan_id} for {request.domain} found no malicious content.")
             final_response = ScanResponse(
                  scan_id=scan_id, status="completed", message="No malicious content found.",
                  domain=request.domain, timestamp=datetime.now(), scan_duration_seconds=round(scan_duration, 2),
                  domain_info=scan_results_data.get('domain_info') # Include domain info even if clean
             )
             scan_cache[scan_id] = final_response
             scan_status["status"] = "completed"
             scan_status["results"] = final_response
        else:
             raise Exception(f"Scan returned unexpected data: {scan_results_data}")

    except Exception as e:
        scan_duration = time.time() - start_time
        logger.error(f"Background scan task {scan_id} failed after {scan_duration:.2f}s: {e}", exc_info=True)
        scan_status["status"] = "failed"
        scan_status["error"] = str(e)
        # Cache the error status
        scan_cache[scan_id] = ScanResponse(scan_id=scan_id, status="failed", message=str(e), domain=request.domain, timestamp=datetime.now())
    finally:
        # Potentially update a database with the final status here
        logger.info(f"Background task for scan {scan_id} finished with status: {scan_status['status']}")


@app.post("/scan", status_code=status.HTTP_202_ACCEPTED)
async def submit_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_user)
):
    """Submit a domain scan request (runs in background)"""
    scan_id = hashlib.md5(f"{request.domain}_{datetime.now().isoformat()}".encode()).hexdigest()[:10]
    logger.info(f"Received scan request {scan_id} for domain {request.domain} from user {current_user.username}")

    # Initial response indicating acceptance
    scan_cache[scan_id] = ScanResponse(scan_id=scan_id, status="processing", domain=request.domain, timestamp=datetime.now())

    # Add the long-running task to the background
    background_tasks.add_task(run_scan_in_background, scan_id, request, current_user)

    return {"scan_id": scan_id, "status": "processing", "message": "Scan submitted. Check status endpoint."}


@app.get("/scan/{scan_id}/status", response_model=ScanResponse)
async def get_scan_status(scan_id: str, current_user: UserInDB = Depends(get_current_user)):
    """Check the status and results of a submitted scan"""
    logger.info(f"User {current_user.username} checking status for scan_id: {scan_id}")
    result = scan_cache.get(scan_id)
    if result:
        # TODO: Add check here to ensure the current_user is allowed to see this scan_id result
        return result
    else:
        # TODO: Check persistent storage (database) if not in cache
        raise HTTPException(status_code=404, detail="Scan ID not found or expired from cache.")


# --- Admin Endpoints ---

@app.post("/admin/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: sqlite3.Connection = Depends(get_db),
    admin_user: UserInDB = Depends(get_current_admin_user)
):
    """Admin: Create a new user"""
    db_user = get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    c = db.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, password_hash, role, organization_name) VALUES (?, ?, ?, ?)",
            (user.username, hashed_password, user.role, user.organization_name)
        )
        db.commit()
        user_id = c.lastrowid
        log_activity(admin_user.username, admin_user.organization_name, "CREATE_USER", f"Created user: {user.username}", db)
        # Fetch the created user to return it
        c.execute("SELECT id, username, role, organization_name, user_api_key FROM users WHERE id = ?", (user_id,))
        new_user_row = c.fetchone()
        return UserResponse.from_orm(new_user_row) # Use .from_orm for Row object
    except sqlite3.IntegrityError:
         raise HTTPException(status_code=400, detail="Username already registered")
    except Exception as e:
         logger.error(f"Error creating user {user.username}: {e}")
         raise HTTPException(status_code=500, detail=f"Could not create user: {e}")


@app.get("/admin/users", response_model=List[UserResponse])
async def read_users(
    skip: int = 0, limit: int = 100,
    db: sqlite3.Connection = Depends(get_db),
    admin_user: UserInDB = Depends(get_current_admin_user)
):
    """Admin: Read list of users"""
    c = db.cursor()
    c.execute("SELECT id, username, role, organization_name, user_api_key FROM users LIMIT ? OFFSET ?", (limit, skip))
    users = c.fetchall()
    return [UserResponse.from_orm(user) for user in users]

@app.get("/admin/logs", response_model=List[LogEntry])
async def read_logs(
    skip: int = 0, limit: int = 50,
    db: sqlite3.Connection = Depends(get_db),
    admin_user: UserInDB = Depends(get_current_admin_user)
):
    """Admin: Read activity logs"""
    c = db.cursor()
    c.execute("SELECT id, timestamp, username, organization_name, action, details FROM activity_log ORDER BY timestamp DESC LIMIT ? OFFSET ?", (limit, skip))
    logs = c.fetchall()
    return [LogEntry.from_orm(log) for log in logs]

# TODO: Add endpoints for Admin to Update and Delete users

# --- Other Endpoints (Adapted) ---

@app.get("/dashboard/stats")
async def get_dashboard_stats(current_user: UserInDB = Depends(get_current_user)):
    """Get dashboard statistics (reads from potentially outdated CSV)"""
    # NOTE: This still reads from CSV. Ideally, should read aggregated data from a scan results DB table.
    try:
        df = data_manager.load_or_create_dataframe() # Reusing your function
        if df.empty:
            return {"total_domains": 0, "total_cases": 0, "infected_domains": 0, "max_cases": 0}

        total_cases = int(df['jumlah_kasus'].sum())
        infected_domains = len(df[df['jumlah_kasus'] > 0])
        max_cases = int(df['jumlah_kasus'].max()) if not df.empty else 0

        return {
            "total_domains": len(df),
            "total_cases": total_cases,
            "infected_domains": infected_domains,
            "max_cases": max_cases
        }
    except Exception as e:
        logger.error(f"Error reading dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve dashboard stats.")


@app.get("/dashboard/ranking")
async def get_domain_ranking(limit: int = Query(10, ge=1, le=100), current_user: UserInDB = Depends(get_current_user)):
     """Get domain rankings (reads from potentially outdated CSV)"""
     # NOTE: This still reads from CSV.
     try:
         df = data_manager.load_or_create_dataframe()
         if df.empty:
             return {"rankings": []}

         df = df.sort_values('jumlah_kasus', ascending=False).head(limit)
         # Convert to list of dicts suitable for JSON
         rankings = df.to_dict('records')
         # Ensure numeric types are standard Python ints for JSON
         for item in rankings:
             for key, val in item.items():
                 if pd.isna(val):
                      item[key] = 0 if isinstance(val, (int, float)) else None # Handle NaN
                 elif isinstance(val, (pd.Timestamp, datetime)):
                      item[key] = val.isoformat() # Format dates
                 elif hasattr(val, 'item'): # Convert numpy types
                      item[key] = val.item()

         return {"rankings": rankings}
     except Exception as e:
         logger.error(f"Error reading dashboard ranking: {e}")
         raise HTTPException(status_code=500, detail="Could not retrieve dashboard ranking.")

@app.get("/domain/{domain}/info")
async def get_domain_info_api(domain: str, current_user: UserInDB = Depends(get_current_user)):
    """Endpoint to get domain intelligence info"""
    # Reusing your core_scanner function
    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(executor, core_scanner.domain_intelligence, domain)
    if 'error' in info:
        raise HTTPException(status_code=404, detail=f"Could not get info for domain: {info['error']}")
    return info

@app.get("/health")
async def health_check():
    # Basic health check, can be expanded
    return {"status": "healthy"}

# --- Run API ---
if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True, # Disable reload in production
        workers=1 # Increase workers based on server cores in production (behind Nginx/Gunicorn)
    )