# AI Agent MCP Test

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that gives Claude real-time internet search, AI-powered summarization, and GitHub integration — built for DevSecOps productivity.

## What it does

This project wires up two external APIs and GitHub as callable tools inside Claude Code:

| Tool | API | What it does |
|------|-----|-------------|
| `search_internet` | Tavily | Live web search — returns titles, URLs, and content |
| `search_internet_with_answer` | Tavily | Advanced search with an AI-generated direct answer |
| `ask_groq` | Groq (Llama 3.3 70B) | Send a prompt to a fast LLM for reasoning or drafting |
| `search_and_summarize` | Tavily + Groq | Search the web, then summarize results with Groq |
| GitHub tools | GitHub API | Read PRs, issues, repos, commits, and more |

## How it works

Claude Code reads `.mcp.json` and spawns the MCP servers as subprocesses on startup. All tool calls flow via the MCP protocol (stdio JSON-RPC) between Claude and the servers.

```
Claude Code
    ↓  MCP (stdio JSON-RPC)
server.py  ──→  Tavily API  →  live search results
           ──→  Groq API    →  LLM response

start_github_mcp.sh  ──→  GitHub API  →  repos, PRs, issues
```

## Setup

### 1. Prerequisites

- Python 3.13+
- Node.js + npx
- A [Tavily API key](https://tavily.com)
- A [Groq API key](https://console.groq.com)
- A GitHub Personal Access Token (scopes: `repo`, `read:org`, `workflow`)

### 2. Install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install mcp tavily-python groq python-dotenv
```

### 3. Configure environment

Create a `.env` file in the project root:

```env
TAVILY_API_KEY=your_tavily_key
GROQ_API_KEY=your_groq_key
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_pat
```

### 4. Open in Claude Code

```bash
claude .
```

Claude Code will automatically detect `.mcp.json` and start the MCP servers. The tools will be available immediately.

## DevSecOps use cases

- **CVE research**: *"search and summarize recent vulnerabilities in nginx 1.24"*
- **PR security review**: *"review the open PRs in my repo and flag any hardcoded secrets"*
- **Incident drafting**: *"ask groq to write an incident summary based on these search results"*
- **Tool evaluation**: *"search and summarize pros and cons of Falco vs Tetragon"*
- **Pipeline debugging**: *"why did the latest GitHub Actions run fail in repo X?"*

## Project structure

```
.
├── server.py              # FastMCP server — Tavily + Groq tools
├── start_github_mcp.sh    # Wrapper script to launch GitHub MCP server
├── .mcp.json              # MCP server config for Claude Code
├── .env                   # API keys (gitignored)
└── .gitignore
```
