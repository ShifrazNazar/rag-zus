"""
Text2SQL service for converting natural language queries to SQL.
Uses LangChain SQLDatabaseChain for safe SQL generation.
"""
import logging
import re
from typing import List, Dict, Any, Optional, Tuple

try:
    from langchain_community.utilities import SQLDatabase
    from langchain_openai import ChatOpenAI
    from langchain.chains import create_sql_query_chain
    from langchain_core.prompts import PromptTemplate
except ImportError:
    SQLDatabase = None
    ChatOpenAI = None
    create_sql_query_chain = None
    PromptTemplate = None

from models.database import engine, Outlet

logger = logging.getLogger(__name__)


class Text2SQLService:
    """Service for converting natural language to SQL queries."""
    
    # Allowed SQL keywords (whitelist approach)
    ALLOWED_KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'LIKE',
        'ORDER', 'BY', 'ASC', 'DESC', 'LIMIT', 'COUNT', 'DISTINCT',
        'IS', 'NULL', 'IS NOT', '=', '!=', '<>', '<', '>', '<=', '>=',
        '(', ')', ',', 'AS', 'GROUP', 'HAVING', 'SUM', 'AVG', 'MAX', 'MIN'
    }
    
    # Blocked keywords (blacklist approach)
    BLOCKED_KEYWORDS = {
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE',
        'EXEC', 'EXECUTE', 'EXECUTE IMMEDIATE', 'MERGE', 'CALL', 'GRANT',
        'REVOKE', 'COMMIT', 'ROLLBACK', 'SAVEPOINT'
    }
    
    def __init__(self, db_uri: Optional[str] = None):
        """
        Initialize Text2SQL service.
        
        Args:
            db_uri: Database URI (defaults to SQLite outlets.db)
        """
        self.db_uri = db_uri or f"sqlite:///data/outlets.db"
        self.db: Optional[SQLDatabase] = None
        self.llm: Optional[ChatOpenAI] = None
        self.chain = None
        
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize database connection and LLM chain."""
        if SQLDatabase is None or ChatOpenAI is None:
            logger.warning("LangChain not available, Text2SQL will be limited")
            return
        
        try:
            # Initialize database connection
            self.db = SQLDatabase(engine, include_tables=['outlets'])
            logger.info("Connected to SQLite database")
            
            # Initialize LLM (will use OpenAI API key from environment)
            try:
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0,
                    verbose=False
                )
                
                # Create SQL query chain with custom prompt
                prompt = PromptTemplate.from_template("""
You are a SQL expert. Given the following database schema and question, generate a SQL query.

Database Schema:
{db_schema}

Question: {question}

Generate a SQL query that:
1. Only uses SELECT statements (no INSERT, UPDATE, DELETE, DROP)
2. Only queries the 'outlets' table
3. Uses proper SQL syntax
4. Returns relevant results

SQL Query:
""")
                
                self.chain = create_sql_query_chain(self.llm, self.db, prompt=prompt)
                logger.info("Text2SQL service initialized")
                
            except Exception as e:
                logger.warning(f"Could not initialize LLM: {e}. Text2SQL will use fallback.")
                self.llm = None
                self.chain = None
                
        except Exception as e:
            logger.error(f"Error initializing Text2SQL service: {e}", exc_info=True)
            self.db = None
    
    def sanitize_sql(self, sql: str) -> str:
        """
        Sanitize SQL query to prevent injection attacks.
        
        Args:
            sql: SQL query string
            
        Returns:
            Sanitized SQL query
            
        Raises:
            ValueError: If query contains blocked keywords
        """
        sql_upper = sql.upper().strip()
        
        # Check for blocked keywords
        for blocked in self.BLOCKED_KEYWORDS:
            if blocked in sql_upper:
                logger.warning(f"Blocked SQL keyword detected: {blocked}")
                raise ValueError(f"SQL query contains blocked keyword: {blocked}")
        
        # Ensure it starts with SELECT
        if not sql_upper.startswith('SELECT'):
            logger.warning("SQL query does not start with SELECT")
            raise ValueError("Only SELECT queries are allowed")
        
        # Ensure it queries outlets table
        if 'FROM OUTLETS' not in sql_upper and 'FROM `OUTLETS`' not in sql_upper:
            logger.warning("SQL query does not query outlets table")
            raise ValueError("Query must target the 'outlets' table")
        
        return sql.strip()
    
    def generate_sql(self, query: str) -> Optional[str]:
        """
        Generate SQL query from natural language.
        
        Args:
            query: Natural language query
            
        Returns:
            SQL query string or None if generation fails
        """
        if self.chain is None:
            logger.warning("SQL chain not initialized, using fallback")
            return self._fallback_sql_generation(query)
        
        try:
            logger.info(f"Generating SQL for query: {query}")
            sql = self.chain.invoke({"question": query})
            
            # Sanitize the generated SQL
            sql = self.sanitize_sql(sql)
            logger.info(f"Generated SQL: {sql}")
            return sql
            
        except Exception as e:
            logger.error(f"Error generating SQL: {e}", exc_info=True)
            return self._fallback_sql_generation(query)
    
    def _fallback_sql_generation(self, query: str) -> Optional[str]:
        """
        Fallback SQL generation using simple pattern matching.
        
        Args:
            query: Natural language query
            
        Returns:
            SQL query string or None
        """
        query_lower = query.lower()
        
        # Simple pattern matching
        if 'petaling jaya' in query_lower or 'pj' in query_lower:
            return "SELECT * FROM outlets WHERE district LIKE '%Petaling Jaya%' OR district LIKE '%PJ%'"
        elif 'kuala lumpur' in query_lower or 'kl' in query_lower:
            return "SELECT * FROM outlets WHERE district LIKE '%Kuala Lumpur%' OR district LIKE '%KL%'"
        elif 'selangor' in query_lower:
            return "SELECT * FROM outlets WHERE district LIKE '%Selangor%'"
        elif 'all' in query_lower or 'list' in query_lower:
            return "SELECT * FROM outlets LIMIT 50"
        else:
            # Generic search in name and location
            return f"SELECT * FROM outlets WHERE name LIKE '%{query}%' OR location LIKE '%{query}%' OR district LIKE '%{query}%' LIMIT 20"
    
    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results.
        
        Args:
            sql: SQL query string
            
        Returns:
            List of outlet dictionaries
        """
        try:
            # Sanitize SQL
            sql = self.sanitize_sql(sql)
            
            # Execute query using SQLAlchemy directly
            from sqlalchemy import text
            from models.database import engine
            
            logger.info(f"Executing SQL: {sql}")
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = result.fetchall()
                
                # Get column names
                columns = result.keys() if hasattr(result, 'keys') else None
                
                # Convert to dictionaries
                results = []
                for row in rows:
                    if columns:
                        # Use column names if available
                        row_dict = dict(zip(columns, row))
                    else:
                        # Fallback to positional access
                        row_dict = {
                            "id": row[0] if len(row) > 0 else None,
                            "name": row[1] if len(row) > 1 else None,
                            "location": row[2] if len(row) > 2 else None,
                            "district": row[3] if len(row) > 3 else None,
                            "hours": row[4] if len(row) > 4 else None,
                            "services": row[5] if len(row) > 5 else None,
                            "lat": float(row[6]) if len(row) > 6 and row[6] is not None else None,
                            "lon": float(row[7]) if len(row) > 7 and row[7] is not None else None,
                        }
                    results.append(row_dict)
                
                logger.info(f"Query returned {len(results)} results")
                return results
                
        except ValueError as e:
            logger.warning(f"SQL sanitization failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error executing SQL query: {e}", exc_info=True)
            return []
    
    def query(self, nl_query: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Convert natural language query to SQL and execute it.
        
        Args:
            nl_query: Natural language query
            
        Returns:
            Tuple of (results, sql_query)
        """
        try:
            # Generate SQL
            sql = self.generate_sql(nl_query)
            
            if sql is None:
                logger.warning("Could not generate SQL query")
                return [], None
            
            # Execute query
            results = self.execute_query(sql)
            
            return results, sql
            
        except Exception as e:
            logger.error(f"Error in Text2SQL query: {e}", exc_info=True)
            return [], None


# Global instance (singleton pattern)
_text2sql_service: Optional[Text2SQLService] = None


def get_text2sql_service() -> Text2SQLService:
    """Get or create the global Text2SQL service instance."""
    global _text2sql_service
    if _text2sql_service is None:
        _text2sql_service = Text2SQLService()
    return _text2sql_service

