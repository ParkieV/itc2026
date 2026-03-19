```shell
# On Ubuntu
sudo apt-get install clang libpq-dev;
# On MacOS
brew install llvm libpq;

# On macOS or Linux
curl -LsSf https://astral.sh/uv/install.sh | sh;
# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install project
uv python pin 3.12;
uv venv;
```