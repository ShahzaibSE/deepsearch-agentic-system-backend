from agents import function_tool, Tool

class SearchTools:
    @classmethod
    @function_tool
    async def search_web(cls, query: str) -> str:
        """
        Search the web for the given query
        """
        try:
            # Input validation
            if not query or not query.strip():
                return "Error: Query cannot be empty. Please provide a valid search term."
            
            query_normalized = query.lower().strip()
            
            # Simple search instruction for LLM
            return f"Search the web for: {query_normalized}. Please provide comprehensive and accurate information about this topic."
            
        except Exception as e:
            return f"Error: Failed to process search query. Please try again with a different term."
