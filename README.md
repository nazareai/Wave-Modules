# Example Agent Module

This is a template module for the Wave Master Agent system. Use this as a starting point for creating your own modules.

## Design Principles

1. **Modularity**: Each module should be completely independent and not rely on specific implementations of other modules
2. **Loose Coupling**: Modules can use context from other modules but should not assume their internal structure
3. **Single Responsibility**: Each module should do one thing well
4. **Extensibility**: Easy to add new operations without changing existing code
5. **Error Handling**: Graceful handling of all error cases
6. **File Management**: Use common directories for consistent file storage across modules
7. **Resource Handling**: Support both local and remote resources uniformly
8. **Query Processing**: Handle file references and operations consistently

## Module Structure

A Wave Master Agent module must have:

1. A `module.py` file containing:
   - A `Module` class that implements `ModuleInterface`
   - `get_capabilities()` method describing the module's functionality
   - `process(query, context)` method to handle queries with proper async support
   - Additional private methods for specific operations
   - Proper event loop handling for async operations

2. Standard response format:
```python
{
    "status": "success" | "error",
    "message": str,  # Human-readable status
    "data": {
        "demo_result": str,  # Human-readable result
        "operation": str,    # What operation was performed
        "result": dict,      # Operation-specific data
        "timestamp": str     # When the operation was performed
    }
}
```

## Resource Handling

The module supports both local and remote resources:

1. **Local Files**:
   ```python
   # Extract file reference
   file_ref = extract_file_reference(query)
   if file_ref and not is_url(file_ref):
       file_path = get_file_path(file_ref, dir_type="files")
   ```

2. **Remote Resources**:
   ```python
   # Handle URLs
   if file_ref and is_url(file_ref):
       # Process remote resource
       result = process_url(file_ref)
   ```

## Query Processing

Queries are processed in a structured way:

1. **Operation Parsing**:
   ```python
   operation, content = self._parse_query(query)
   ```

2. **File Reference Extraction**:
   ```python
   file_ref = extract_file_reference(content)
   if file_ref:
       content = {
           "file_ref": file_ref,
           "file_path": get_file_path(file_ref),
           "is_url": is_url(file_ref),
           "query": content.replace(file_ref, "").strip()
       }
   ```

## Common Directory Usage

The module uses the common directory structure for file management:

1. **Files Directory** (`files/`):
   - For persistent shared files
   - Used by `save` operation
   - Analysis results and generated content
   ```python
   from master_agent.common import get_file_path
   file_path = get_file_path("example.txt", dir_type="files")
   ```

2. **Downloads Directory** (`downloads/`):
   - For downloaded content
   - Used by `download` operation
   ```python
   download_path = get_file_path("data.json", dir_type="downloads")
   ```

3. **Temporary Directory** (`temp/`):
   - For temporary files
   - Used for intermediate processing
   ```python
   temp_path = get_file_path("temp.txt", dir_type="temp")
   ```

## Creating a New Module

1. Create a new directory under `master_agent/modules/` with your module name
2. Copy this example module as a template
3. Define your module's operations in `__init__`
4. Implement operation handlers as private methods
5. Follow the standard patterns for:
   - Query parsing
   - Operation handling
   - Context usage
   - Error handling
   - Progress feedback
   - File management
   - Resource handling

## Context Handling

Modules should handle context generically and safely:

```python
def process(self, query: str, context: Optional[Dict[str, Any]] = None):
    if context:
        for module_name, module_data in context.items():
            if isinstance(module_data, dict):
                # Look for specific types of data
                if "content" in module_data:
                    # Handle content
                if "metadata" in module_data:
                    # Handle metadata
```

## Operation Structure

Define operations in a modular way:

```python
class Module(ModuleInterface):
    def __init__(self):
        self.supported_operations = {
            "process": self._process_text,
            "analyze": self._analyze_data,
            "extract": self._extract_info
        }
    
    def _process_text(self, content: Any, context: Optional[Dict] = None):
        # Handle both direct content and file references
        if isinstance(content, dict):
            file_ref = content["file_ref"]
            query = content["query"]
        else:
            file_ref = None
            query = content
```

## Example Usage

```python
# Initialize the module
module = Module()

# Get capabilities
capabilities = module.get_capabilities()
print(f"Supported operations: {capabilities['supported_operations']}")

# Process different types of queries
results = [
    module.process("process: Hello World"),
    module.process("analyze: data.txt"),
    module.process("analyze: https://example.com/data.json"),
    module.process("extract: what topics are in document.txt")
]
```

## Testing Your Module

Test these scenarios:

1. Basic operations without context
2. Operations with various context data
3. Invalid operations
4. Malformed queries
5. Edge cases (empty input, huge input)
6. Local file operations
7. Remote resource operations
8. Context handling with missing or invalid data

## Best Practices

1. **Operation Design**
   - Clear, single-purpose operations
   - Consistent naming scheme
   - Well-documented inputs and outputs
   - Support both local and remote resources

2. **Context Usage**
   - Don't assume other modules exist
   - Handle missing context gracefully
   - Document what context enhances operation
   - Type check all context data

3. **Error Handling**
   - Clear error messages
   - Helpful suggestions
   - Graceful fallbacks
   - Resource cleanup

4. **Documentation**
   - Document each operation
   - Provide usage examples
   - Explain context usage
   - Document resource handling

5. **File Management**
   - Use appropriate common directories
   - Clean up temporary files
   - Handle file operations safely
   - Support both local and remote resources

6. **Response Structure**
   - Consistent format
   - Operation-specific data
   - Clear status messages
   - Include resource information

## Integration Testing

Test your module with these scenarios:

1. Basic query without context
2. Query with context from other modules
3. Local file operations
4. Remote resource operations
5. Error handling cases
6. Edge cases (empty query, invalid input)
7. File operations in each directory type
8. Context handling with various data types

## Async Operation Handling

The module properly handles asynchronous operations:

1. **Event Loop Management**:
   ```python
   # Get or create event loop
   try:
       loop = asyncio.get_event_loop()
   except RuntimeError:
       loop = asyncio.new_event_loop()
       asyncio.set_event_loop(loop)
   ```

2. **Nested Event Loops**:
   ```python
   # Allow nested event loops for compatibility
   import nest_asyncio
   nest_asyncio.apply()
   ```

3. **Async Operation Handling**:
   ```python
   # Handle both sync and async operations
   if asyncio.iscoroutinefunction(handler):
       # Run async handler in event loop
       result = loop.run_until_complete(handler(content, context))
   else:
       # Call sync handler directly
       result = handler(content, context)
   ```

4. **Best Practices**:
   - Use `nest_asyncio` for nested event loop support
   - Handle both sync and async operation handlers
   - Properly detect coroutine functions
   - Clean up resources after async operations
   - Work seamlessly with master_agent's event loop

## Contributing

When creating a new module:

1. Follow the standard structure
2. Add comprehensive documentation
3. Include example queries
4. Test thoroughly
5. Use common directories appropriately
6. Support both local and remote resources
7. Handle context data safely 
