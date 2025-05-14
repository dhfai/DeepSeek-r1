from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime
import logging
from pathlib import Path

from ..config.config import MEMORY_STORE_CONFIG

class MemoryStoreManager:
    def __init__(self):
        self.memory_file = Path(MEMORY_STORE_CONFIG["persist_directory"]) / "memory.json"
        self.max_items = MEMORY_STORE_CONFIG["max_memory_items"]
        self.logger = logging.getLogger(__name__)
        self._initialize_memory_store()

    def _initialize_memory_store(self):
        """Initialize memory store file if it doesn't exist"""
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            if not self.memory_file.exists():
                with open(self.memory_file, 'w') as f:
                    json.dump({"memories": []}, f)
            self.logger.info("Memory store initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing memory store: {str(e)}")
            raise

    def _load_memories(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load memories from file"""
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading memories: {str(e)}")
            raise

    def _save_memories(self, data: Dict[str, List[Dict[str, Any]]]):
        """Save memories to file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving memories: {str(e)}")
            raise

    def add_memory(self, memory_type: str, content: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """
        Add a new memory

        Args:
            memory_type (str): Type of memory (e.g., 'feedback', 'interaction')
            content (Dict[str, Any]): Memory content
            metadata (Dict[str, Any], optional): Additional metadata
        """
        try:
            data = self._load_memories()

            # Create new memory entry
            memory = {
                "type": memory_type,
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }

            # Add to memories list
            data["memories"].append(memory)

            # Trim if exceeding max items
            if len(data["memories"]) > self.max_items:
                data["memories"] = data["memories"][-self.max_items:]

            self._save_memories(data)
            self.logger.info(f"Successfully added new memory of type: {memory_type}")
        except Exception as e:
            self.logger.error(f"Error adding memory: {str(e)}")
            raise

    def get_memories(self, memory_type: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get memories, optionally filtered by type

        Args:
            memory_type (str, optional): Filter by memory type
            limit (int, optional): Limit number of results

        Returns:
            List[Dict[str, Any]]: List of memories
        """
        try:
            data = self._load_memories()
            memories = data["memories"]

            # Filter by type if specified
            if memory_type:
                memories = [m for m in memories if m["type"] == memory_type]

            # Apply limit if specified
            if limit:
                memories = memories[-limit:]

            return memories
        except Exception as e:
            self.logger.error(f"Error getting memories: {str(e)}")
            raise

    def update_memory(self, memory_id: str, updates: Dict[str, Any]):
        """
        Update an existing memory

        Args:
            memory_id (str): ID of memory to update
            updates (Dict[str, Any]): Updates to apply
        """
        try:
            data = self._load_memories()

            # Find and update memory
            for memory in data["memories"]:
                if memory.get("id") == memory_id:
                    memory.update(updates)
                    memory["last_updated"] = datetime.now().isoformat()
                    break

            self._save_memories(data)
            self.logger.info(f"Successfully updated memory: {memory_id}")
        except Exception as e:
            self.logger.error(f"Error updating memory: {str(e)}")
            raise

    def clear_memories(self, memory_type: Optional[str] = None):
        """
        Clear all memories or memories of specific type

        Args:
            memory_type (str, optional): Clear only memories of this type
        """
        try:
            data = self._load_memories()

            if memory_type:
                data["memories"] = [m for m in data["memories"] if m["type"] != memory_type]
            else:
                data["memories"] = []

            self._save_memories(data)
            self.logger.info(f"Successfully cleared memories" +
                           (f" of type: {memory_type}" if memory_type else ""))
        except Exception as e:
            self.logger.error(f"Error clearing memories: {str(e)}")
            raise
