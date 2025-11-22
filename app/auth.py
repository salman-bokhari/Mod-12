from fastapi import Header, HTTPException
from typing import Optional

def get_current_user(db=Depends(get_db), authorization: Optional[str] = Header(None)):
    # Expect header: "Bearer <token>"
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    try:
        scheme, token = authorization.split()
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    user = db.query(models.User).filter(models.User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

