import re

with open("app/main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add imports for auth
auth_imports = """
from app.auth import get_current_user, create_access_token, verify_password
from app.models import User
from fastapi.security import OAuth2PasswordRequestForm
"""
if "from app.auth import" not in content:
    content = content.replace("from contextlib import asynccontextmanager", auth_imports + "\nfrom contextlib import asynccontextmanager")

# Add login endpoint
login_endpoint = """
@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

"""
if "@app.post(\"/api/login\")" not in content:
    content = content.replace("# ----------------- FastAPI Endpoints -----------------", "# ----------------- FastAPI Endpoints -----------------\n" + login_endpoint)

# Inject current_user dependency into all route functions
def inject_dep(match):
    prefix = match.group(1) # e.g. 'def get_dashboard('
    args = match.group(2)   # e.g. 'db: Session = Depends(get_db)'
    suffix = match.group(3) # e.g. '):'
    
    # Don't inject into login
    if "def login(" in prefix:
        return match.group(0)
    
    if "current_user" in args:
        return match.group(0)
        
    return f"{prefix}{args}, current_user: User = Depends(get_current_user){suffix}"

content = re.sub(r'(def [a-zA-Z0-9_]+\(.*?(?:db: Session = Depends\(get_db\)).*?)(\)):', inject_dep, content)

with open("app/main.py", "w", encoding="utf-8") as f:
    f.write(content)
