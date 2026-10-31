# Kamolika MCP Server - Global Registration

This project provides a globally accessible MCP (Model Context Protocol) server implementation for Book.Backend backend.

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip package manager

### Core Files

```
mcpbangla/
├── kamolika.py          # Python MCP client for Book.Backend
├── global_mcp_server.py # Global MCP server backend
├── server.py           # Lightweight MCP HTTP server
├── mcp_config.json     # Configuration reference
└── README.md           # This file
```

## Register as MCP Server

### Method 1: Start as Background Service

```bash
# Start the global MCP server on port 6469
python mcpbangla/global_mcp_server.py 6469

# Or use alternative port
python mcpbangla/global_mcp_server.py 6468
```

The server registers itself as a globally accessible endpoint that all `kamolika.py` clients will automatically discover.

### Method 2: Register Programmatically

```python
from mcpbangla.global_mcp_server import get_mcp_client

# Get the registered global MCP client
client = get_mcp_client("localhost", 6469)

# Use with any tool
result = client.call("expand_idea", '{"seed": "time travel story"}')
```

## Using the Kamolika Client

### One-shot Commands

```bash
# Initialize connection
python mcpbangla/kamolika.py init

# List available tools
python mcpbangla/kamolika.py tools

# Call a tool
python mcpbangla/kamolika.py call expand_idea '{"seed": "AI future"}'

# Get dashboard
python mcpbangla/kamelika.py call get_dashboard {}

# List all tools first
python mcpbangla/kamelika.py tools
python mcpbangla/kamelika.py call write_book '{"bookName": "MyStory"}'
```

### Interactive REPL Mode

```bash
python mcpbangla/kamolika.py
```

Type commands like:
- `init` - Initialize MCP connection
- `tools` - List available tools
- `call <tool> [args]` - Execute a tool
- `help` - Show help text
- `quit` - Exit REPL mode

## Available Tools

The global server registers these tools automatically:

| Tool | Description | Parameters |
|------|-------------|------------|
| `write_book` | Write or update a book | `bookName` (string) |
| `get_dashboard` | Get dashboard information | None |
| `expand_idea` | Expand an idea into a story | `seed` (string) |
| `suggest_book_name` | Suggest a book name from gist | `gist` (string) |
| `get_book` | Retrieve an existing book | `bookName` (string) |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Global MCP Server Backend                   │
│              (mcpbangla/global_mcp_server.py)                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓ HTTP/gRPC connection
┌─────────────────────────────────────────────────────────────┐
│                    Kamolika MCP Client                         │
│                 (mcpbangla/kamolika.py)                         │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

Edit `mcpbangla/mcp_config.json` to customize:

- Server URL and port
- Tool configurations
- Authentication settings

## Troubleshooting

### Connection Issues

1. Verify the MCP server is running on the expected port
2. Ensure no other service is using port 6469 or 6468
3. Check firewall settings

### Tool Not Found

- Ensure `global_mcp_server.py` has been started as a background service
- All registered tools become available through `kamolika.py tools` command

## License

MIT License - See `LICENSE` file for details
