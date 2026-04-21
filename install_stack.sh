#!/bin/bash
set -e
echo "🛡️ Vixero Agentic Stack Installer"
echo "=================================="

# 1. Node.js (required for OpenClaw + Claude Code)
echo "📦 Installing Node.js v22..."
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
node --version
npm --version

# 2. Claude Code
echo "🤖 Installing Claude Code..."
npm install -g @anthropic-ai/claude-code
claude --version

# 3. OpenClaw
echo "🦾 Installing OpenClaw..."
npm install -g openclaw
openclaw --version

# 4. Docker + NVIDIA Container Toolkit (for dockerizing later)
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

echo "✅ Core stack installed!"
echo "Versions:"
node --version
npm --version
claude --version
openclaw --version
docker --version
