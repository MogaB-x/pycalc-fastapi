from fastapi import APIRouter, HTTPException, Depends, status
import bcrypt
from jose import jwt
from models.users import UserLogin, UserRegister
from db.db_connection import get_db
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()

SECRET_KEY = "ultra-quantum-secret-key"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60


@router.post("/register")
async def register(user: UserRegister):
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM users WHERE username=?", (user.username,)
    )
    existing_user = await cursor.fetchone()
    await cursor.close()

    if existing_user:
        await db.close()
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = bcrypt.hashpw(
        user.password.encode('utf-8'),
        bcrypt.gensalt()
    )
    await db.execute(
        "INSERT INTO users "
        "(username, password, email, role) "
        "VALUES (?, ?, ?, ?)",
        (user.username, hashed_password, user.email, user.role)
    )
    await db.commit()
    await db.close()

    return {"message": "User registered successfully"}


@router.post("/login")
async def login(user: UserLogin):
    db = await get_db()
    cursor = await db.execute(
        "SELECT password FROM users WHERE username=? ", (user.username,)
    )
    result = await cursor.fetchone()
    await cursor.close()
    await db.close()

    if not result:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    hased_password = result[0]
    if not bcrypt.checkpw(user.password.encode('utf-8'), hased_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    payload = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


security = HTTPBearer()


def verify_token(
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@router.get("/secure-history")
async def get_secure_history(current_user: str = Depends(verify_token)):
    db = await get_db()

    # Verify the user role and fetch operations
    cursor = await db.execute(
        "SELECT role, id FROM users WHERE username=?",
        (current_user,)
    )
    user = await cursor.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    role, user_id = user

    if role == "admin":
        cursor = await db.execute(
            "SELECT operation, input, result, timestamp, user_id "
            "FROM operations ORDER BY id DESC")
    else:
        cursor = await db.execute(
            "SELECT operation, input, result, timestamp "
            "FROM operations "
            "WHERE user_id=? ORDER BY id DESC", (user_id, )
        )

    rows = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return {"user": current_user, "role": role, "history": rows}


@router.delete("/delete-user/{username}")
async def delete_user(
        username: str,
        current_user: str = Depends(verify_token)
):
    db = await get_db()
    cursor = await db.execute(
        "SELECT role FROM users WHERE username=?",
        (current_user,)
    )
    user_role = await cursor.fetchone()
    await cursor.close()

    if not user_role or user_role[0] != "admin":
        await db.close()
        raise HTTPException(
            status_code=403,
            detail="Only admins can delete users"
        )

    cursor = await db.execute(
        "SELECT id FROM users WHERE username=?",
        (username,)
    )
    user_id = await cursor.fetchone()
    await cursor.close()

    if not user_id:
        await db.close()
        raise HTTPException(status_code=404, detail="User not found")

    await db.execute("DELETE FROM users WHERE id=?", (user_id[0],))
    await db.commit()
    await db.close()

    return {"message": f"User {username} deleted successfully"}
