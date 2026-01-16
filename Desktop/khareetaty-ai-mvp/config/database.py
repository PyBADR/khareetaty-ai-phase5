"""
Database connection utilities for Khareetaty AI
Provides consistent database access with proper error handling
"""
import psycopg2
from contextlib import contextmanager
from typing import Generator, Optional, Any
import pandas as pd
from config.settings import DATABASE
from config.logging import get_module_logger

logger = get_module_logger("database")

@contextmanager
def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """Context manager for database connections with automatic cleanup"""
    conn = None
    try:
        conn = psycopg2.connect(
            host=DATABASE.HOST,
            port=DATABASE.PORT,
            dbname=DATABASE.NAME,
            user=DATABASE.USER,
            password=DATABASE.PASSWORD
        )
        conn.autocommit = False  # Explicit transaction control
        logger.debug("Database connection established")
        yield conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")

def execute_query(query: str, params: Optional[tuple] = None) -> list:
    """Execute a SELECT query and return results"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                results = cur.fetchall()
                logger.info(f"Query executed successfully, returned {len(results)} rows")
                return results
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise

def execute_command(query: str, params: Optional[tuple] = None) -> int:
    """Execute an INSERT/UPDATE/DELETE command and return affected rows"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                affected_rows = cur.rowcount
                conn.commit()
                logger.info(f"Command executed successfully, affected {affected_rows} rows")
                return affected_rows
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        raise

def execute_many(query: str, params_list: list) -> int:
    """Execute many commands with parameter lists"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(query, params_list)
                affected_rows = cur.rowcount
                conn.commit()
                logger.info(f"Bulk command executed successfully, affected {affected_rows} rows")
                return affected_rows
    except Exception as e:
        logger.error(f"Bulk command execution failed: {e}")
        raise

def query_to_dataframe(query: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """Execute query and return results as pandas DataFrame"""
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            logger.info(f"Query converted to DataFrame with {len(df)} rows")
            return df
    except Exception as e:
        logger.error(f"DataFrame query failed: {e}")
        raise

def health_check() -> bool:
    """Check database connectivity"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                return result[0] == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

def create_tables_if_not_exists():
    """Ensure all required tables exist"""
    try:
        # This would typically load from a SQL file
        # For now, we'll check if the main tables exist
        table_check_query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'incidents_raw'
            );
        """
        result = execute_query(table_check_query)
        if result and result[0][0]:
            logger.info("Database tables already exist")
            return True
        else:
            logger.warning("Database tables not found - run migrations first")
            return False
    except Exception as e:
        logger.error(f"Table existence check failed: {e}")
        return False

# Reusable database connection for legacy code compatibility
def get_legacy_db_params():
    """Get database parameters for legacy code compatibility"""
    return {
        "host": DATABASE.HOST,
        "port": DATABASE.PORT,
        "dbname": DATABASE.NAME,
        "user": DATABASE.USER,
        "password": DATABASE.PASSWORD
    }