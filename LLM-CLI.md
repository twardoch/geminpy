# LLM CLI

# LLM CLI Tools Suite

A powerful collection of command-line tools that brings AI coding assistants from Claude (Anthropic), Gemini (Google), and Codex (OpenAI) directly to your terminal. These tools enable AI-powered development workflows with the ability to run multiple LLMs in parallel for enhanced productivity and comparison.

## 1. What Are LLM CLI Tools?

LLM CLI tools are command-line interfaces that connect large language models directly to your local development environment. Unlike web-based AI assistants, these tools:

- **Run locally in your terminal** - No context switching between browser and code editor
- **Understand your entire codebase** - Can read, analyze, and modify files in context
- **Execute commands safely** - Run shell commands with configurable safety levels
- **Maintain project awareness** - Stay aware of your project structure and dependencies
- **Support multimodal inputs** - Accept text, screenshots, and diagrams

## 2. Why Use Multiple LLMs?

Using multiple LLMs in parallel offers several advantages:

1. **Specialized Capabilities** - Each model excels at different tasks:
   - **Claude**: Superior at complex reasoning and code understanding
   - **Gemini**: Excellent for creative solutions and multimodal tasks
   - **Codex**: Optimized specifically for code generation and debugging

2. **Redundancy & Validation** - Compare outputs from different models to ensure accuracy
3. **Rate Limit Management** - Distribute workload across providers to avoid hitting limits
4. **Cost Optimization** - Use cheaper models for simple tasks, premium models for complex ones
5. **Diverse Perspectives** - Different models may approach problems uniquely

## 3. Prerequisites

### 3.1. Installation on macOS

```bash
brew install parallel uv; npm i -g @google/gemini-cli @anthropic-ai/claude-code @openai/codex; uv pip install --system geminpy
```

### 3.2. API Keys Required

You may need to set up your API keys as environment variables, but: 

- Claude also works with a Claude Pro or Max subscription, and you’ll authenticate once
- Gemini also works with a Gemini Pro subscription, and you’ll authenticate once (or you may need to authenticate each time)
- Codex works with an OpenAI subscription, and is billed per token, but you may get 1M or 10M daily free tokens if you [enable sharing](https://platform.openai.com/settings/organization/data-controls/sharing)

```bash
export ANTHROPIC_API_KEY="your-claude-api-key"
export GEMINI_API_KEY="your-gemini-api-key"  
export OPENAI_API_KEY="your-openai-api-key"
```

## 4. Tool Overview

### 4.1. Single Execution Tools

These tools run a single LLM on your prompt:

- **`llmask-cla`** - Claude CLI wrapper
- **`llmask-gem`** - Gemini CLI wrapper  
- **`llmask-cod`** - Codex CLI wrapper
- **`llmask`** - Unified interface (specify model or use "random")

### 4.2. Parallel Execution Tools

These tools run multiple instances in parallel across directories:

- **`llmulti-cla`** - Parallel Claude execution
- **`llmulti-gem`** - Parallel Gemini execution
- **`llmulti-cod`** - Parallel Codex execution
- **`llmulti`** - Unified parallel interface

## 5. Usage Guide

### 5.1. Basic Single Model Usage

```bash
# Use Claude to refactor code in current directory
llmask cla "Refactor this code to use async/await patterns"

# Use Gemini with a specific directory
llmask gem "Explain the architecture of this project" --dir /path/to/project

# Use Codex for bug fixing
llmask cod "Find and fix the memory leak in this code"

# Let the system randomly choose a model
llmask random "Write unit tests for the utils module"
```

### 5.2. Parallel Processing

Process multiple directories with the same prompt:

```bash
# Create a file listing directories to process
echo "/project1" > dirs.txt
echo "/project2" >> dirs.txt
echo "/project3" >> dirs.txt

# Run Claude on all directories in parallel
llmulti cla dirs.txt "Update all dependencies to latest versions"

# Compare outputs from different models
llmulti random dirs.txt "Analyze code quality and suggest improvements"
```

## 6. How It Works

### 6.1. Architecture

1. **Wrapper Scripts** (`llmask-*`):
   - Handle directory navigation
   - Parse command-line arguments
   - Set up proper environment
   - Call underlying LLM CLI with appropriate flags

2. **Unified Interface** (`llmask`):
   - Routes to appropriate LLM based on selection
   - Supports random model selection for A/B testing
   - Maintains consistent interface across models

3. **Parallel Execution** (`llmulti`):
   - Uses GNU `parallel` for efficient multi-processing
   - Distributes work across up to 8 concurrent processes
   - Maintains separate contexts for each directory

### 6.2. Safety Features

All tools implement safety measures:

- **Claude Code**: Asks for permission before file changes
- **Gemini CLI**: Runs network-disabled and directory-sandboxed
- **Codex**: Configurable approval modes (suggest/auto-edit/full-auto)

## 7. Common Use Cases

### 7.1. Code Refactoring
```bash
llmask cla "Refactor this React class component to use hooks"
```

### 7.2. Bug Detection and Fixing
```bash
llmask cod "Find potential null pointer exceptions and fix them"
```

### 7.3. Documentation Generation
```bash
llmask gem "Generate comprehensive API documentation for all public methods"
```

### 7.4. Architecture Analysis
```bash
llmask random "Analyze the current architecture and suggest improvements"
```

### 7.5. Parallel Test Generation
```bash
# Generate tests for multiple microservices
llmulti cla services.txt "Write comprehensive unit tests with >80% coverage"
```

### 7.6. Comparative Analysis
```bash
# Get different perspectives on optimization
for model in cla gem cod; do
  llmask $model "Suggest performance optimizations for this module"
done
```

## 8. Advanced Features

### 8.1. Custom Configurations

Each tool supports configuration files:

- Claude: `.claude/config.json`
- Gemini: `GEMINI.md` in project root
- Codex: `.codex/config.json`

### 8.2. Model-Specific Options

**Claude Code**:
- Supports MCP (Model Context Protocol) servers
- Can integrate with GitHub, GitLab
- Maintains conversation context

**Gemini CLI**:
- 1 million token context window
- Free tier: 60 requests/min, 1000/day
- Supports Google Search grounding

**Codex**:
- Multiple approval modes
- Multimodal input support
- Sandbox execution environment

## 9. Best Practices

1. **Start with Clear Prompts**: Be specific about what you want
2. **Use Appropriate Models**: 
   - Complex reasoning → Claude
   - Creative solutions → Gemini  
   - Code-specific tasks → Codex
3. **Review Outputs**: Always review AI-generated changes
4. **Iterate Gradually**: Make incremental changes rather than massive refactors
5. **Leverage Parallelism**: Use `llmulti` for repetitive tasks across projects

## 10. Troubleshooting

### 10.1. Common Issues

1. **API Key Errors**: Ensure environment variables are set correctly
2. **Rate Limits**: Distribute load using parallel tools or wait between requests
3. **Context Length**: Break large tasks into smaller chunks
4. **Directory Permissions**: Ensure tools have read/write access as needed

### 10.2. Performance Tips

- Use `--dir` flag to avoid unnecessary directory changes
- Keep prompts concise for faster processing
- Use configuration files to avoid repeating settings
- Monitor API usage to optimize costs

## 11. Security Considerations

- **Code stays local**: Your source code never leaves your machine unless explicitly shared
- **Sandboxed execution**: Commands run in restricted environments
- **API-only communication**: Only prompts and high-level context sent to providers
- **Version control friendly**: All changes trackable through git

## 12. Contributing

These wrapper scripts are designed to be extensible. To add support for new LLMs:

1. Create a new wrapper script following the `llmask-*` pattern
2. Implement the same argument parsing structure
3. Add the model to the selection arrays in `llmask` and `llmulti`
4. Test with both single and parallel execution modes

## 13. License

The wrapper scripts are provided as-is for convenience. Individual LLM tools have their own licenses:
- Claude Code: Proprietary (usage via API)
- Gemini CLI: Apache 2.0 (open source)
- Codex: Proprietary (usage via API)

## 14. Future Enhancements

Potential improvements to consider:

- Result aggregation and comparison tools
- Cost tracking and optimization
- Automated prompt templates
- Integration with CI/CD pipelines
- Support for additional LLM providers
- Unified configuration management


## 15. Single execution

### 15.1. `llmask-cla`

```sh
#!/usr/bin/env bash

# Process --dir argument if present
CWD="."
while [[ $# -gt 0 ]]; do
    case "$1" in
    --dir)
        if [[ -n "$2" ]]; then
            CWD="$2"
            shift 2
        else
            echo "Error: --dir requires a directory argument" >&2
            exit 1
        fi
        ;;
    *)
        break
        ;;
    esac
done

cd "$CWD"

claude --add-dir "$CWD" --dangerously-skip-permissions -p "$@"
```

### 15.2. `llmask-cod`

```sh
#!/usr/bin/env bash

# Process --dir argument if present
CWD="."
args=()
while [[ $# -gt 0 ]]; do
    case "$1" in
    --dir)
        CWD="$2"
        shift 2
        ;;
    *)
        args+=("$1")
        shift
        ;;
    esac
done

# Change to specified directory
cd "$CWD"

# Run codex with remaining args
codex -m "o4-mini" --dangerously-auto-approve-everything --full-auto -w "." -a "full-auto" -q "${args[@]}" | jq -r 'select(.role == "assistant") | .content[] | select(.type == "output_text") | .text'
```

### 15.3. `llmask-gem`

```sh
#!/usr/bin/env bash
# Process --dir argument if present
CWD="."

while [[ $# -gt 0 ]]; do
    case "$1" in
    --dir)
        if [[ -n "$2" ]]; then
            CWD="$2"
            shift 2
        else
            echo "Error: --dir requires a directory argument" >&2
            exit 1
        fi
        ;;
    *)
        break
        ;;
    esac
done
cd "$CWD"

geminpy -a -y -p "$@"
```

### 15.4. `llmask`

```sh
#!/usr/bin/env bash

# Get the model type, handling random case
model="${1}"
if [ "${model}" = "random" ]; then
    # Array of valid models
    models=("cod" "gem" "cla")
    # Get random index
    rand_idx=$((RANDOM % 3))
    model="${models[rand_idx]}"
elif [ "${model}" != "cod" ] && [ "${model}" != "gem" ] && [ "${model}" != "cla" ]; then
    echo "Error: Model must be one of: cod, gem, cla, random" >&2
    exit 1
fi

# Shift off the model argument and pass remaining args to the chosen llmask tool
shift
llmask-${model} "$@"
```

## 16. Parallel execution

### 16.1. `llmulti-cla`

```sh
#!/usr/bin/env bash
llmulti cla "${1}" "${2}"
```

### 16.2. `llmulti-cod`

```sh
#!/usr/bin/env bash
llmulti cod "${1}" "${2}"
```

### 16.3. `llmulti-gem`

```sh
#!/usr/bin/env bash
llmulti gem "${1}" "${2}"
```

### 16.4. `llmulti`

```sh
#!/usr/bin/env bash

# Get the model type, handling random case
model="${1}"
if [ "${model}" = "random" ]; then
    # Array of valid models
    models=("cod" "gem" "cla")
    # Get random index
    rand_idx=$((RANDOM % 3))
    model="${models[rand_idx]}"
elif [ "${model}" != "cod" ] && [ "${model}" != "gem" ] && [ "${model}" != "cla" ]; then
    echo "Error: Model must be one of: cod, gem, cla, random" >&2
    exit 1
fi

parallel -j 8 llmask-${model} \""${3}"\" --dir "{}" ::: $(<"${2}")
```

---

