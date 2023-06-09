from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
        )

    async def execute(
            self,
            command,
            *args,
            fetch: bool = False,
            fetchval: bool = False,
            fetchrow: bool = False,
            execute: bool = False,
    ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        phone_number VARCHAR(20) UNIQUE,
        booked_pc SMALLINT UNIQUE,
        debt INTEGER DEFAULT 0
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_computers(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Computers (
        id SERIAL PRIMARY KEY,
        price SMALLINT NOT NULL DEFAULT 6000,
        available BOOLEAN DEFAULT TRUE,
        is_booked BOOLEAN NOT NULL DEFAULT FALSE,
        customer_id BIGINT,
        booking_time_start DATE,
        booking_time_end DATE
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join(
            [f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)]
        )
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, username, telegram_id):
        sql = "INSERT INTO Users (full_name, username, telegram_id) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, full_name, username, telegram_id, fetchrow=True)

    async def add_pc(self, price):
        sql = "INSERT INTO Computers (price) VALUES ($1) returning *"
        return await self.execute(sql, price, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_all_computers(self):
        sql = "SELECT * FROM Computers"
        return await self.execute(sql, fetch=True)

    async def select_free_pc(self):
        sql = "SELECT * FROM Computers WHERE is_booked = FALSE AND available = TRUE"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_pc(self, pc_id):
        sql = "SELECT * FROM Computers WHERE id = $1"
        return await self.execute(sql, pc_id, fetchrow=True)

    async def select_debtors(self):
        sql = "SELECT * FROM Users WHERE debt != 0"
        return await self.execute(sql, fetch=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def select_computers(self):
        sql = "SELECT id FROM Computers ORDER BY id ASC"
        return await self.execute(sql, fetch=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def update_user_phone_number(self, phone_number, telegram_id):
        sql = "UPDATE Users SET phone_number=$1 WHERE telegram_id=$2"
        return await self.execute(sql, phone_number, telegram_id, execute=True)

    async def update_user_debt(self, debt: int, telegram_id):
        sql = "UPDATE Users SET debt=$1 WHERE telegram_id=$2"
        return await self.execute(sql, debt, telegram_id, execute=True)

    async def update_pc_price(self, new_price, pc_id):
        sql = "UPDATE Computers SET price=$1 WHERE id = $2"
        return await self.execute(sql, new_price, pc_id, execute=True)

    async def update_pc_availability(self, pc_id):
        sql = "UPDATE Computers SET available = NOT available WHERE id = $1"
        return await self.execute(sql, pc_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def delete_pc(self, pc_id):
        await self.execute("DELETE FROM Computers WHERE id = $1", pc_id, execute=True)

    async def clean_pc_list(self):
        await self.execute("DELETE FROM Computers WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE IF EXISTS Users", execute=True)

    async def drop_computers(self):
        await self.execute("DROP TABLE IF EXISTS  Computers", execute=True)
