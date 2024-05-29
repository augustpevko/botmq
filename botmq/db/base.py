from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class Base(ABC):
    """
    Abstract base class for database operations.
    """
    @abstractmethod
    def connect(self):
        """Connect to the database."""
        pass

    @abstractmethod
    def close(self):
        """Close the connection to the database."""
        pass

    @abstractmethod
    def create_table(self):
        """Create new table(s) in the database."""
        pass

    @abstractmethod
    def add_group(self, group_name: str, password: str):
        """
        Add a new group to the table.
        
        Args:
            group_name (str): The name of the group.
            password (str): The password for the group.
        """
        pass

    @abstractmethod
    def add_user(self, user_id: int, password: str):
        """
        Add a user to a group if the passwords match.
        
        Args:
            user_id (int): The ID of the user.
            password (str): The password of the user.
        """
        pass

    @abstractmethod
    def delete_group(self, group_name: str):
        """
        Delete a group by its name.
        
        Args:
            group_name (str): The name of the group to delete.
        """
        pass

    @abstractmethod
    def delete_user(self, user_id: int, group_name: str):
        """
        Delete a user from a group.
        
        Args:
            user_id (int): The ID of the user.
            group_name (str): The name of the group.
        """
        pass

    @abstractmethod
    def get_user(self, group_name: str) -> Optional[List[int]]:
        """
        Return user ID(s) from a group name.
        
        Args:
            group_name (str): The name of the group.
        
        Returns:
            Optional[List[int]]: List of user IDs in the group.
        """
        pass

    @abstractmethod
    def get_group(self, user_id: int) -> List[str]:
        """
        Return group name(s) by user ID.
        
        Args:
            user_id (int): The ID of the user.
        
        Returns:
            List[str]: List of group names the user belongs to.
        """
        pass

    @abstractmethod
    def list_groups(self) -> List[str]:
        """
        Return a list of all groups.
        
        Returns:
            List[str]: List of all group names.
        """
        pass

    @abstractmethod
    def list_users(self) -> List[int]:
        """
        Return a list of all users.
        
        Returns:
            List[int]: List of all user IDs.
        """
        pass

    @abstractmethod
    def set_config(self, user_id: int, config: Dict):
        """
        Set a user's configuration by user ID.
        
        Args:
            user_id (int): The ID of the user.
            config (Dict): The configuration settings.
        """
        pass

    @abstractmethod
    def get_config(self, user_id: int) -> Optional[Dict]:
        """
        Return a user's configuration by user ID.
        
        Args:
            user_id (int): The ID of the user.
        
        Returns:
            Optional[Dict]: The configuration settings of the user.
        """
        pass
