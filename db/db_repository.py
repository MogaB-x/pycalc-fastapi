from db.db_connection import get_db


async def insert_operation(
        operation: str,
        input_data: str,
        result_data: str,
        username: str):
    db = await get_db()
    cursor = await db.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    )
    user_row = await cursor.fetchone()
    if not user_row:
        await db.close()
        raise Exception("User not found in database")

    user_id = user_row[0]
    await db.execute(
        "INSERT INTO operations (operation, input, result, user_id) "
        "VALUES (?, ?, ?, ?)",
        (operation, input_data, result_data, user_id)
    )
    await db.commit()
    await db.close()


async def get_all_operations():
    db = await get_db()
    cursor = await db.execute(
        "SELECT operation, input, result, timestamp "
        "FROM operations ORDER BY timestamp DESC"
    )
    rows = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return rows
