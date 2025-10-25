# Installing SCC (Sloc Cloc and Code)

SCC is a fast, accurate code counter with complexity calculations and COCOMO estimates.

## Installation Options

### Option 1: Download Binary (Recommended)

```bash
# Download latest release
cd /tmp
wget https://github.com/boyter/scc/releases/download/v3.1.0/scc_3.1.0_Linux_x86_64.tar.gz

# Extract
tar -xzf scc_3.1.0_Linux_x86_64.tar.gz

# Move to system path
sudo mv scc /usr/local/bin/

# Verify installation
scc --version
```

### Option 2: Using Snap (Ubuntu/Debian)

```bash
sudo snap install scc
```

### Option 3: Using Go

```bash
go install github.com/boyter/scc/v3@latest
```

### Option 4: Using Homebrew (macOS/Linux)

```bash
brew install scc
```

## Verification

After installation, verify SCC is working:

```bash
scc --version
scc /path/to/your/repo
```

## Usage in Repo Analyzer

The repository analyzer will automatically detect if SCC is installed and use it for:

- Accurate lines of code counting
- Code complexity analysis
- Language detection
- Enhanced COCOMO II cost estimation

If SCC is not installed, the analyzer will fall back to basic estimation methods.

## Benefits

- **Fast**: Written in Go, extremely fast even on large repositories
- **Accurate**: More accurate than traditional tools like cloc
- **Comprehensive**: Counts code, comments, blanks, and complexity
- **Cost Estimation**: Built-in COCOMO cost estimation
- **Many Languages**: Supports 200+ programming languages

## More Information

- GitHub: https://github.com/boyter/scc
- Documentation: https://github.com/boyter/scc#scc-sloc-cloc-and-code
