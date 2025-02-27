#!/bin/bash

set -e

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Install oh-my-zsh if not already installed
echo -e "${BLUE}Installing oh-my-zsh...${NC}"

if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo -e "${BLUE}Installing oh-my-zsh...${NC}"
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

    # Install additional zsh plugins
    echo -e "${BLUE}Installing additional zsh plugins...${NC}"
    git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
    git clone https://github.com/zsh-users/zsh-completions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-completions

    # Configure oh-my-zsh plugins
    sed -i 's/plugins=(git)/plugins=(git python pip docker docker-compose aws zsh-autosuggestions zsh-syntax-highlighting zsh-completions)/' ~/.zshrc
else
    echo -e "${BLUE}oh-my-zsh already installed${NC}"
fi

# Always check and update theme if it's devcontainers
if grep -q 'ZSH_THEME="devcontainers"' ~/.zshrc; then
    echo -e "${BLUE}Updating ZSH theme to robbyrussell...${NC}"
    sed -i 's/ZSH_THEME="devcontainers"/ZSH_THEME="robbyrussell"/' ~/.zshrc
fi

# Check if Git email is configured
current_email=$(git config --global user.email || echo "")
if [ -z "$current_email" ]; then
    echo -e "${BLUE}Setting up Git configuration...${NC}"
    echo -e "${GREEN}Enter your Git email address (default: timothy.sabat@gmail.com):${NC}"
    read git_email
    git_email=${git_email:-"timothy.sabat@gmail.com"}
    git config --global user.email "$git_email"
else
    echo -e "${BLUE}Git email already configured as:${NC} $current_email"
fi

# Check if Git name is configured
current_name=$(git config --global user.name || echo "")
if [ -z "$current_name" ]; then
    echo -e "${GREEN}Enter your Git name (default: tsabat):${NC}"
    read git_name
    git_name=${git_name:-"tsabat"}
    git config --global user.name "$git_name"
else
    echo -e "${BLUE}Git name already configured as:${NC} $current_name"
fi

# Always set default branch to main
git config --global init.defaultBranch main

# Configure Git editor to vim
git config --global core.editor "vim"

# Configure Git editor and diff/merge tools
git config --global diff.tool "vimdiff"
git config --global merge.tool "vimdiff"
git config --global difftool.prompt false
git config --global merge.conflictstyle "diff3"
git config --global alias.d "difftool"

# Show diff in commit message editor
git config --global commit.verbose true
git config --global commit.status true

# Configure Git to use SSH instead of HTTPS
git config --global url."git@github.com:".insteadOf "https://github.com/"

# Continue with the rest of the setup
poetry config virtualenvs.in-project true
poetry install
poetry run pre-commit install

# Add aliases to zshrc
printf "\nalias ll='ls -lahSr --color=auto'\n" >> ~/.zshrc

poetry run ruff check --select I,F401 --fix --exit-zero
poetry run ruff format

# Remind about Python interpreter selection
echo -e "\n${YELLOW}IMPORTANT: Remember to select your Python interpreter:${NC}"
echo -e "1. Press ${GREEN}Cmd/Ctrl + Shift + P${NC}"
echo -e "2. Type ${GREEN}Python: Select Interpreter${NC}"
echo -e "3. Choose the interpreter from ${GREEN}.venv/bin/python${NC}\n"
