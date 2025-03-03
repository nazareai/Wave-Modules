from typing import Dict, Any, Optional
import time
from pathlib import Path
import re
import asyncio
import nest_asyncio
from master_agent.core.module_interface import ModuleInterface
from master_agent.common import get_file_path, extract_file_reference, is_url

class Module(ModuleInterface):
    """Example module demonstrating the standard structure for Wave Master Agent modules.
    
    This template shows how to:
    1. Implement the required interface
    2. Handle context from other modules generically
    3. Process queries and return structured responses
    4. Use common directories for file storage
    5. Handle errors gracefully
    6. Process both local and remote resources
    7. Handle file references in queries
    8. Handle async operations and event loops properly
    """
    
    def __init__(self):
        """Initialize the module with supported operations."""
        # Allow nested event loops for compatibility with other async code
        nest_asyncio.apply()
        
        self.supported_operations = {
            "process": self._process_text,
            "analyze": self._analyze_data,
            "generate": self._generate_content,
            "save": self._save_file,
            "download": self._download_content,
            "extract": self._extract_info
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return information about the module's capabilities.
        
        This method should clearly describe:
        - What the module does
        - What types of queries it can handle
        - Example queries that work well
        - Supported file types and operations
        """
        return {
            "description": "Example module that demonstrates the standard module structure and best practices",
            "capabilities": [
                "Process text from files or direct input",
                "Analyze data from local or remote sources",
                "Generate content based on input and context",
                "Save files to common storage",
                "Download and process remote content",
                "Extract information from documents"
            ],
            "supported_operations": list(self.supported_operations.keys()),
            "supported_files": {
                "local": [".txt", ".json", ".csv", ".md"],
                "remote": ["http://", "https://"],
                "context": ["any"]
            },
            "example_queries": [
                "process: Hello World",
                "analyze: data.txt",
                "analyze: https://example.com/data.json",
                "generate: content about AI",
                "save: example.txt:This is content to save",
                "download: https://example.com/data.json",
                "extract: what topics are in document.txt"
            ]
        }
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a query with optional context from other modules.
        
        This method demonstrates proper handling of async operations and event loops:
        1. Gets or creates an event loop
        2. Runs async operations properly
        3. Handles both sync and async operations
        4. Works with both standalone and master_agent execution
        
        Args:
            query: The user's query string
            context: Optional dictionary containing results from other modules
                    Each module's data structure is considered opaque to this module
        
        Returns:
            Dictionary containing:
            - status: "success" or "error"
            - message: Human-readable status message
            - data: Dictionary containing:
                - demo_result: Human-readable result
                - [other keys]: Module-specific structured data
        """
        try:
            # 1. Parse operation and content
            operation, content = self._parse_query(query)
            
            # 2. Show processing feedback
            print(f"  🔄 Processing {operation} operation...")
            
            # 3. Check if operation is supported
            if operation not in self.supported_operations:
                return {
                    "status": "error",
                    "message": f"Unsupported operation: {operation}",
                    "data": {
                        "supported_operations": list(self.supported_operations.keys()),
                        "suggestion": "Try one of the supported operations"
                    }
                }
            
            # 4. Extract any file references
            file_ref = extract_file_reference(content)
            if file_ref:
                # Handle the file reference appropriately
                file_path = get_file_path(file_ref, dir_type="files")
                content = {
                    "file_ref": file_ref,
                    "file_path": file_path,
                    "is_url": is_url(file_ref),
                    "query": content.replace(file_ref, "").strip() or "Please process this content"
                }
            
            # 5. Get or create event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # 6. Process the operation (handle both sync and async)
            handler = self.supported_operations[operation]
            if asyncio.iscoroutinefunction(handler):
                # If handler is async, run it in the event loop
                result = loop.run_until_complete(handler(content, context))
            else:
                # If handler is sync, just call it directly
                result = handler(content, context)
            
            # 7. Return structured response
            return {
                "status": "success",
                "message": f"Successfully processed {operation} operation",
                "data": {
                    "demo_result": f"{operation.capitalize()}: {result['output']}",
                    "operation": operation,
                    "result": result,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            
        except Exception as e:
            # Handle any unexpected errors
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}",
                "data": {
                    "error_type": "unexpected_error",
                    "query_received": query,
                    "suggestion": "Please check the query format: operation: content"
                }
            }
    
    def _parse_query(self, query: str) -> tuple[str, str]:
        """Parse the operation and content from the query.
        
        Expected format: "operation: content"
        Default operation is "process" if no operation specified.
        """
        if ":" in query:
            operation, content = query.split(":", 1)
            return operation.strip().lower(), content.strip()
        return "process", query.strip()
    
    def _process_text(self, content: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle text processing operation."""
        print("  📝 Processing text...")
        
        # Handle both direct text and file references
        text_content = content if isinstance(content, str) else content.get("query", "")
        file_ref = content.get("file_ref") if isinstance(content, dict) else None
        
        # Example: Save processed text to temp directory
        temp_file = get_file_path("processed_text.txt", dir_type="temp")
        temp_file.write_text(f"""
Processed at {time.strftime('%Y-%m-%d %H:%M:%S')}
Source: {file_ref if file_ref else 'Direct input'}
Content: {text_content}
        """.strip())
        
        return {
            "output": f"Processed {'file' if file_ref else 'text'} and saved to {temp_file.name}",
            "source": file_ref or "direct_input",
            "length": len(text_content),
            "temp_file": str(temp_file),
            "context_used": bool(context)
        }
    
    def _analyze_data(self, content: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle data analysis operation."""
        print("  🔍 Analyzing data...")
        
        # Handle both direct content and file references
        if isinstance(content, dict):
            source = content["file_ref"]
            query = content["query"]
            is_remote = content["is_url"]
        else:
            source = "direct_input"
            query = content
            is_remote = False
        
        # Example: Save analysis results to files directory
        results_file = get_file_path("analysis_results.txt", dir_type="files")
        
        # Example of generic context usage
        context_summary = []
        if context:
            for module_name, module_data in context.items():
                if isinstance(module_data, dict):
                    # Look for useful data without assuming structure
                    if "content" in module_data:
                        context_summary.append(f"Content from {module_name}")
                    if "metadata" in module_data:
                        context_summary.append(f"Metadata from {module_name}")
        
        # Save analysis results
        analysis_content = f"""
Analysis Results
---------------
Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
Source: {source} ({'remote' if is_remote else 'local'})
Query: {query}
Context Sources: {', '.join(context_summary) if context_summary else 'None'}
        """.strip()
        results_file.write_text(analysis_content)
        
        return {
            "output": f"Analyzed {'remote' if is_remote else 'local'} data and saved results",
            "source": source,
            "query": query,
            "context_sources": context_summary if context else [],
            "results_file": str(results_file)
        }
    
    def _generate_content(self, content: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle content generation operation."""
        print("  ✨ Generating content...")
        
        # Handle both direct content and file references
        topic = content if isinstance(content, str) else content.get("query", "")
        
        # Example: Save generated content to files directory
        output_file = get_file_path(f"generated_{int(time.time())}.txt", dir_type="files")
        
        # Example of using context to enhance generation
        enhancements = []
        if context:
            for module_name, module_data in context.items():
                if isinstance(module_data, dict):
                    if "content" in module_data:
                        enhancements.append(f"Enhanced with content from {module_name}")
                    if "metadata" in module_data:
                        enhancements.append(f"Using metadata from {module_name}")
        
        generated_content = f"""
Generated Content
----------------
Topic: {topic}
Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
Enhancements: {', '.join(enhancements) if enhancements else 'None'}

This is an example of generated content about {topic}.
The content can be enhanced with context from other modules.
        """.strip()
        
        output_file.write_text(generated_content)
        
        return {
            "output": f"Generated content about {topic}",
            "topic": topic,
            "enhancements": enhancements,
            "output_file": str(output_file)
        }
    
    def _save_file(self, content: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle file saving operation."""
        print("  💾 Saving file...")
        
        # Parse filename and content
        if isinstance(content, str):
            if ":" not in content:
                raise ValueError("Save operation requires format: filename:content")
            filename, file_content = content.split(":", 1)
        else:
            filename = content.get("file_ref")
            file_content = content.get("query")
            
        if not filename or not file_content:
            raise ValueError("Both filename and content are required")
        
        # Clean and save
        filename = filename.strip()
        file_content = file_content.strip()
        
        # Save to files directory
        output_file = get_file_path(filename, dir_type="files")
        output_file.write_text(file_content)
        
        return {
            "output": f"Saved content to {output_file.name}",
            "file_path": str(output_file),
            "size": len(file_content)
        }
    
    def _download_content(self, content: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle content download operation."""
        print("  ⬇️ Downloading content...")
        
        # Get URL from content
        url = content if isinstance(content, str) else content.get("file_ref")
        if not url or not is_url(url):
            raise ValueError("Valid URL is required for download operation")
        
        # Simulate download by saving to downloads directory
        filename = Path(url).name or "downloaded_content.txt"
        download_file = get_file_path(filename, dir_type="downloads")
        
        # Simulate downloaded content
        downloaded_content = f"""
Downloaded Content
----------------
Source: {url}
Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
Status: Success
Query: {content.get('query') if isinstance(content, dict) else 'None'}
        """.strip()
        
        download_file.write_text(downloaded_content)
        
        return {
            "output": f"Downloaded content from {url}",
            "source": url,
            "download_path": str(download_file),
            "size": len(downloaded_content)
        }
    
    def _extract_info(self, content: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle information extraction operation."""
        print("  🔍 Extracting information...")
        
        # Handle both direct content and file references
        if isinstance(content, dict):
            source = content["file_ref"]
            query = content["query"]
            is_remote = content["is_url"]
        else:
            source = "direct_input"
            query = content
            is_remote = False
        
        # Example: Save extraction results
        output_file = get_file_path(f"extracted_{int(time.time())}.txt", dir_type="files")
        
        # Example of advanced context usage
        context_data = []
        if context:
            for module_name, module_data in context.items():
                if isinstance(module_data, dict):
                    # Look for specific types of data
                    if "content" in module_data:
                        context_data.append(("content", module_name))
                    if "metadata" in module_data:
                        context_data.append(("metadata", module_name))
                    if "answer" in module_data:
                        context_data.append(("answer", module_name))
        
        # Save extraction results
        extraction_content = f"""
Extraction Results
-----------------
Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
Source: {source} ({'remote' if is_remote else 'local'})
Query: {query}
Context Used: {', '.join(f"{type} from {module}" for type, module in context_data)}

This is a demonstration of information extraction.
The extraction can be enhanced with context from other modules.
        """.strip()
        
        output_file.write_text(extraction_content)
        
        return {
            "output": f"Extracted information from {source}",
            "source": source,
            "query": query,
            "context_data": context_data,
            "output_file": str(output_file)
        } 