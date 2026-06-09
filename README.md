# LamaBang

A fast, multi-threaded scanner that discovers publicly accessible [Ollama](https://ollama.com/) servers and identifies which AI models are available on them — with no authentication required - Free :)

## What It Does

Given a list of `ip:port` targets, the tool:

1. Checks if the server is reachable
2. Queries `/api/tags` to list available models
3. Tests each model with a lightweight generation request to confirm it's auth-free
4. Saves any working servers and their models to an output file

## Requirements

- Python 3.7+
- See `requirements.txt`

## Installation

```bash
git clone https://github.com/yourusername/ollama-free-model-finder.git
cd ollama-free-model-finder
pip install -r requirements.txt
```

## Usage

```bash
python scanner.py -i targets.txt -o results.txt
```

### Arguments

| Flag | Description | Default |
|------|-------------|---------|
| `-i`, `--input` | Input file with one `ip:port` per line | *(required)* |
| `-o`, `--output` | Output file to save found servers | *(required)* |
| `-t`, `--threads` | Number of concurrent threads | `10` |
| `-v`, `--verbose` | Show step-by-step checking output | `False` |

### Example

```bash
# Basic scan
python scanner.py -i targets.txt -o results.txt

# Faster scan with more threads
python scanner.py -i targets.txt -o results.txt -t 50

# Verbose mode to see what's happening
python scanner.py -i targets.txt -o results.txt -v
```

### Input File Format (`targets.txt`)

```
192.168.1.10:11434
10.0.0.5:11434
203.0.113.42:11434
```

### Output Format (`results.txt`)

```
192.168.1.10:11434 -> llama3.2:latest, mistral:latest
203.0.113.42:11434 -> gemma3:latest
```

## Example Output

```
[1/100] [-] 10.0.0.1:11434
[2/100] 10.0.0.2:11434 -> llama3.2:latest, mistral:latest
[3/100] [-] 10.0.0.3:11434
...
Done. 3 server(s) with models found out of 100 checked.
```

## Notes

- Default connection timeout is **5 seconds** per server
- Generation test timeout is **10 seconds** per model
- Only servers with at least one **auth-free** model are saved to output
- Results are written incrementally — safe to interrupt and resume with a new input list

## Legal & Ethical Use

This tool is intended for **research, network auditing, and educational purposes only**. Only scan IP ranges you own or have explicit permission to scan. Unauthorised scanning of third-party systems may be illegal in your jurisdiction.

## License

MIT
