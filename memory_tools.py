from agno.tools import Toolkit
from memory import insert_memories, recall_memories

class MemoryToolkit(Toolkit):
    """
    A toolkit for inserting and recalling memories using the memory module.
    """

    def __init__(self):
        super().__init__(name="memory_tools", tools=[self.insert, self.recall])

    def insert(self, memories):
        """
        Insert one or more memories into the memory collection.
        :param memories: List of memory strings to insert.
        :return: None
        """
        insert_memories(memories)
        return "Memories inserted successfully."

    def recall(self, query, num_results=3):
        """
        Recall relevant memories from the memory collection.
        :param query: The query string to search for relevant memories.
        :param num_results: Number of results to return.
        :return: Formatted string of recalled memories.
        """
        return recall_memories(query, num_results=num_results)