import logging
import json
import psycopg2
from psycopg2 import sql
from hashlib import sha256
from typing import Any, Dict, List, Optional

from .base import Base

class ConnectionNotEstablishedError(Exception):
    """Exception raised when the database connection is not established."""
    pass

class PostgreSQL(Base):
    """
    Derived class for PostgreSQL database interaction.
    """
    def __init__(self, connection_params: Dict[str, Any]):
        """Initialize the PostgreSQL object with connection parameters."""
        self.connection_params = connection_params
        self.connection = None
        self.cursor = None

    def rollback(self) -> None:
        """
        Roll back the current database transaction.
        
        Raises:
            ConnectionNotEstablishedError: If the database connection is not established.
        """
        if not self.connection:
            raise ConnectionNotEstablishedError('Database connection has not been established.')
        self.connection.rollback()

    def connect(self) -> None:
        """
        Connect to the database.
        
        Raises:
            Exception: If there is an error while connecting to the database.
        """
        try:
            self.connection = psycopg2.connect(**self.connection_params)
        except Exception as e:
            logging.error(f'Error connecting to the database: {e}')
            return
        if not self.connection:
            raise ConnectionNotEstablishedError('Database connection has not been established.')
        self.cursor = self.connection.cursor()
        logging.info('Connected to the PostgreSQL database')

    def close(self) -> None:
        """Close the connection to the database."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logging.info('Connection to the PostgreSQL database closed')

    def create_table(self) -> None:
        """
        Create new table(s) in the database.
        
        Raises:
            ConnectionNotEstablishedError: If the database connection is not established.
        """
        if not self.connection or not self.cursor:
            raise ConnectionNotEstablishedError('Database connection has not been established.')
        query = """
            CREATE TABLE IF NOT EXISTS groups (
                id SERIAL PRIMARY KEY,
                group_name VARCHAR(255) UNIQUE,
                password VARCHAR(64)
            );

            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE,
                config JSON
            );

            CREATE TABLE IF NOT EXISTS user_groups (
                user_id BIGINT,
                group_name VARCHAR(255),
                PRIMARY KEY (user_id, group_name),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (group_name) REFERENCES groups(group_name)
            );
        """
        self.cursor.execute(query)
        self.connection.commit()
        logging.info('Tables created successfully')

    def add_group(self, group_name: str, password: str) -> None:
        """
        Add a new group to the table.
        
        Args:
            group_name (str): The name of the group.
            password (str): The password for the group.
            
        Raises:
            ConnectionNotEstablishedError: If the database connection is not established.
        """
        if not self.connection or not self.cursor:
            raise ConnectionNotEstablishedError('Database connection has not been established.')
        hashed_password = sha256(password.encode()).hexdigest()
        query = sql.SQL("INSERT INTO groups (group_name, password) VALUES ({}, {});").format(
            sql.Literal(group_name),
            sql.Literal(hashed_password)
        )
        self.cursor.execute(query)
        self.connection.commit()

    def add_user(self, user_id: int, password: str) -> str:
        """
        Add a user to a group if the passwords match.
        
        Args:
            user_id (int): The ID of the user.
            password (str): The password of the user.
            
        Returns:
            str: Result message indicating the outcome.
            
        Raises:
            ConnectionNotEstablishedError: If the database connection is not established.
        """
        if not self.connection or not self.cursor:
            raise ConnectionNotEstablishedError('Database connection has not been established.')
        hashed_password = sha256(password.encode()).hexdigest()

        # Check if the password exists in the groups table
        query = sql.SQL("SELECT group_name FROM groups WHERE password = {};").format(
            sql.Literal(hashed_password)
        )
        self.cursor.execute(query)
        matching_groups = [result[0] for result in self.cursor.fetchall()]

        if matching_groups: 
            for matching_group in matching_groups:
                # Check if the user already exists in the users table
                query = sql.SQL("SELECT user_id FROM users WHERE user_id = {};").format(
                    sql.Literal(user_id)
                )
                self.cursor.execute(query)
                existing_user = self.cursor.fetchone()

                if existing_user:
                    # If user exists, add the group to the user's list
                    query = sql.SQL("INSERT INTO user_groups (user_id, group_name) VALUES ({}, {});").format(
                        sql.Literal(user_id),
                        sql.Literal(matching_group)
                    )
                    self.cursor.execute(query)
                    self.connection.commit()
                    result_message = f"User added to group '{matching_group}'"
                    logging.info(result_message)
                    return result_message
                else:
                    # If user does not exist, create a new user and add the group
                    query = sql.SQL("INSERT INTO users (user_id, config) VALUES ({}, NULL);").format(
                        sql.Literal(user_id)
                    )
                    self.cursor.execute(query)
                    query = sql.SQL("INSERT INTO user_groups (user_id, group_name) VALUES ({}, {});").format(
                        sql.Literal(user_id),
                        sql.Literal(matching_group)
                    )
                    self.cursor.execute(query)
                    self.connection.commit()
                    result_message = f"User created and added to group '{matching_group}'"
                    logging.info(result_message)
                    return result_message
        result_message = 'No matching group found for the provided password' 
        logging.info(result_message)
        return result_message

    def delete_group(self, group_name: str) -> None:
        """
        Delete a group by its name.
        
        Args:
            group_name (str): The name of the group to delete.
            
        Raises:
            ConnectionNotEstablishedError: If the database connection is not established.
        """
        if not self.connection or not self.cursor:
            raise ConnectionNotEstablishedError('Database connection has not been established.')
        # Delete entries from user_groups table first
        query_user_groups = sql.SQL("DELETE FROM user_groups WHERE group_name = {};").format(
            sql.Literal(group_name)
        )
        self.cursor.execute(query_user_groups)
        self.connection.commit()

        # Now delete the group from the groups table
        query_groups = sql.SQL("DELETE FROM groups WHERE group_name = {};").format(
            sql.Literal(group_name)
        )
        self.cursor.execute(query_groups)
        self.connection.commit()

    def delete_user(self, user_id: int, group_name: str) -> None:
        """
        Delete a user from a group.
        
        Args:
            user_id (int): The ID of the user.
            group_name (str): The name of the group.
            
        Raises:
            ConnectionNotEstablishedError: If the database connection is not established.
        """
        if not self.connection or not self.cursor:
            raise ConnectionNotEstablishedError('Database connection has not been established.')
        # Delete entry from user_groups table first
        query_user_groups = sql.SQL("DELETE FROM user_groups WHERE user_id = {} AND group_name = {};").format(
            sql.Literal(user_id),
            sql.Literal(group_name)
        )
        self.cursor.execute(query_user_groups)
        self.connection.commit()

        # Now, delete the user from the users table if no more groups are associated
        query_users = sql.SQL("DELETE FROM users WHERE user_id = {} AND NOT EXISTS (SELECT 1 FROM user_groups WHERE user_id = {});").format(
            sql.Literal(user_id),
            sql.Literal(user_id)
        )
        self.cursor.execute(query_users)
        self.connection.commit()

    def get_user(self, group_name: str) -> Optional[List[int]]:
        """
        Return user ID(s) from a group name.
        
        Args:
            group_name (str): The name of the group.
            
        Returns:
            List[int]: List of user IDs in the group.
                                 
        Raises:
            ConnectionNotEstablishedError: If the database connection is not established.
        """
        if not self.cursor:
            raise ConnectionNotEstablishedError('Database connection has not been established.')
        query = sql.SQL("SELECT user_id FROM user_groups WHERE group_name = {};").format(
            sql.Literal(group_name)
        )
        self.cursor.execute(query)
        return [result[0] for result in self.cursor.fetchall()]

    def get_group(self, user_id: int) -> List[str]:
        """
        Return group name(s) by user ID.
        
        Args:
            user_id (int): The ID of the user.
            
        Returns:
            List[str]: List of group names the user belongs to.
            
        Raises:
            ConnectionNotEstablishedError: If the database connection is not established.
        """
        if not self.cursor:
            raise ConnectionNotEstablishedError('Database connection has not been established.')
        query = sql.SQL("SELECT group_name FROM user_groups WHERE user_id = {};").format(
            sql.Literal(user_id)
        )
        self.cursor.execute(query)
        return [result[0] for result in self.cursor.fetchall()]
    
    def list_groups(self) -> List[str]:
        """
        Return a list of all groups.
        
        Returns:
            List[str]: List of all group names.
            
        Raises:
            ConnectionNotEstablishedError: If the database connection is not established.
        """
        if not self.cursor:
            raise ConnectionNotEstablishedError('Database connection has not been established.')
        query = sql.SQL("SELECT DISTINCT group_name FROM groups;")
        self.cursor.execute(query)
        return [result[0] for result in self.cursor.fetchall()]

    def list_users(self) -> List[int]:
        """
        Return a list of all users.
        
        Returns:
            List[int]: List of all user IDs.
            
        Raises:
            ConnectionNotEstablishedError: If the database connection is not established.
        """
        if not self.cursor:
            raise ConnectionNotEstablishedError('Database connection has not been established.')
        query = sql.SQL("SELECT DISTINCT user_id FROM users;") 
        self.cursor.execute(query)
        return [result[0] for result in self.cursor.fetchall()]
    
    def set_config(self, user_id: int, config: Dict) -> None:
        """
        Set a user's configuration by user ID.
        
        Args:
            user_id (int): The ID of the user.
            config (Dict): The configuration settings.
            
        Raises:
            ConnectionNotEstablishedError: If the database connection is not established.
        """
        if not self.connection or not self.cursor:
            raise ConnectionNotEstablishedError('Database connection has not been established.')
        json_config = json.dumps(config)
        query = sql.SQL("UPDATE users SET config = {} WHERE user_id = {};").format(
            sql.Literal(json_config),
            sql.Literal(user_id)
        )
        self.cursor.execute(query)
        self.connection.commit()

    def get_config(self, user_id: int) -> Optional[Dict]:
        """
        Return a user's configuration by user ID.
        
        Args:
            user_id (int): The ID of the user.
        
        Returns:
            Optional[Dict]: The configuration settings of the user.
                            
        Raises:
            ConnectionNotEstablishedError: If the database connection is not established.
        """
        if not self.cursor:
            raise ConnectionNotEstablishedError('Database connection has not been established.')
        query = sql.SQL("SELECT config FROM users WHERE user_id = {};").format(
            sql.Literal(user_id)
        )
        self.cursor.execute(query)
        result = self.cursor.fetchone()

        if result:
            config = result[0]
            if config is not None:
                return config
            else:
                logging.info(f'Config for user {user_id} is NULL')
                return None
        else:
            logging.error(f'No config found for user {user_id}')
            return None