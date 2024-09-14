import asyncpg
from strings import stories
from decouple import config

pool = None


async def init_db_pool():
    global pool
    pool = await asyncpg.create_pool(config('POSTGRES_DSN'))


async def create_table():
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                name TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                deposit INTEGER DEFAULT 0
            )
        ''')


async def add_user(user_id, name):
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)

        if not user:
            await conn.execute('INSERT INTO users (user_id, name, points, deposit) VALUES ($1, $2, $3, $4)',
                               user_id, name, 100, 0)


async def get_user_info(user_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)


async def update_user_points(user_id, new_points):
    async with pool.acquire() as conn:
        await conn.execute('UPDATE users SET points = $1 WHERE user_id = $2', new_points, user_id)


async def update_user_deposit(user_id, new_deposit):
    async with pool.acquire() as conn:
        await conn.execute('UPDATE users SET deposit = $1 WHERE user_id = $2', new_deposit, user_id)


async def get_all_users():
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT user_id, deposit FROM users')
        return rows


async def get_all_points():
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT name, points FROM users')
        return rows

message_mapping = {}
message_reactions = {}

# user_points = {356384042: 100}
# user_contributions = {}

restricted_users = {}

user_selected_task = {}
message_ids_to_delete = {}

available_shortcut_tasks = [
    stories.get("task1_short"),
    stories.get("task2_short"),
    stories.get("task3_short"),
]

available_text_tasks = [
    stories.get("task1_short"),
    stories.get("task3_short"),
]

available_media_tasks = [
    stories.get("task2_short")
]
