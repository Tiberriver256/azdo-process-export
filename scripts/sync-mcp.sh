#!/bin/bash

# Script to sync MCP servers from VS Code config to Claude Code
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required but not installed${NC}"
    echo "Install with: brew install jq (macOS) or apt-get install jq (Ubuntu)"
    exit 1
fi

# Check if claude command is available
if ! command -v claude &> /dev/null; then
    echo -e "${RED}Error: claude command not found${NC}"
    echo "Make sure Claude Code is installed and in your PATH"
    exit 1
fi

# Find VS Code MCP config file (workspace only)
VSCODE_CONFIG=".vscode/mcp.json"
if [ ! -f "$VSCODE_CONFIG" ]; then
    echo -e "${RED}Error: No workspace MCP config found${NC}"
    echo "Looking for .vscode/mcp.json in current directory"
    exit 1
fi

echo -e "${GREEN}Found VS Code MCP config: $VSCODE_CONFIG${NC}"

# Check if config has MCP servers
if ! jq -e '.servers' "$VSCODE_CONFIG" > /dev/null 2>&1; then
    echo -e "${RED}Error: No MCP servers found in config${NC}"
    exit 1
fi

# Get server names
SERVER_NAMES=$(jq -r '.servers | keys[]' "$VSCODE_CONFIG")

if [ -z "$SERVER_NAMES" ]; then
    echo -e "${YELLOW}No MCP servers to sync${NC}"
    exit 0
fi

echo -e "${GREEN}Found MCP servers:${NC}"
echo "$SERVER_NAMES" | sed 's/^/  - /'

# Function to add MCP server to Claude Code
add_mcp_server() {
    local server_name="$1"
    local config_path="$2"
    
    # Extract server config
    local server_config=$(jq -r ".servers[\"$server_name\"]" "$config_path")
    
    # Detect transport type
    local transport=$(echo "$server_config" | jq -r '.type // "stdio"')
    local url=$(echo "$server_config" | jq -r '.url // empty')
    local command=$(echo "$server_config" | jq -r '.command // empty')
    
    # Build claude mcp add command with local scope (project-specific)
    local claude_cmd="claude mcp add \"$server_name\" -s local"
    
    # Handle different transport types
    case "$transport" in
        "sse")
            if [ -z "$url" ]; then
                echo -e "${RED}  ✗ Skipping $server_name: SSE transport requires URL${NC}"
                return 1
            fi
            claude_cmd="$claude_cmd --transport sse \"$url\""
            ;;
        "http")
            if [ -z "$url" ]; then
                echo -e "${RED}  ✗ Skipping $server_name: HTTP transport requires URL${NC}"
                return 1
            fi
            claude_cmd="$claude_cmd --transport http \"$url\""
            ;;
        "stdio"|*)
            if [ -z "$command" ]; then
                echo -e "${RED}  ✗ Skipping $server_name: stdio transport requires command${NC}"
                return 1
            fi
            claude_cmd="$claude_cmd \"$command\""
            
            # Add args if they exist
            local args=$(echo "$server_config" | jq -r '.args[]? // empty')
            if [ -n "$args" ]; then
                while IFS= read -r arg; do
                    if [ -n "$arg" ]; then
                        claude_cmd="$claude_cmd \"$arg\""
                    fi
                done <<< "$args"
            fi
            ;;
    esac
    
    # Add environment variables if they exist
    local env_vars=$(echo "$server_config" | jq -r '.env // {} | to_entries[] | "\(.key)=\(.value)"')
    if [ -n "$env_vars" ]; then
        while IFS= read -r env_var; do
            if [ -n "$env_var" ]; then
                claude_cmd="$claude_cmd -e \"$env_var\""
            fi
        done <<< "$env_vars"
    fi
    
    echo -e "${YELLOW}  Adding: $server_name ($transport)${NC}"
    echo "    Command: $claude_cmd"
    
    # Execute the command
    if eval "$claude_cmd"; then
        echo -e "${GREEN}  ✓ Successfully added $server_name${NC}"
        return 0
    else
        echo -e "${RED}  ✗ Failed to add $server_name${NC}"
        return 1
    fi
}

# Process each server
SUCCESS_COUNT=0
FAIL_COUNT=0

echo -e "\n${GREEN}Syncing MCP servers to Claude Code...${NC}"

while IFS= read -r server_name; do
    if add_mcp_server "$server_name" "$VSCODE_CONFIG"; then
        ((SUCCESS_COUNT++))
    else
        ((FAIL_COUNT++))
    fi
    echo
done <<< "$SERVER_NAMES"

# Summary
echo -e "${GREEN}Sync complete!${NC}"
echo -e "  ✓ Successfully synced: $SUCCESS_COUNT servers"
if [ $FAIL_COUNT -gt 0 ]; then
    echo -e "  ✗ Failed: $FAIL_COUNT servers"
fi

# Show current Claude Code MCP status
echo -e "\n${GREEN}Current Claude Code MCP servers:${NC}"
if claude mcp list 2>/dev/null; then
    true
else
    echo "Run 'claude mcp list' to see configured servers"
fi
