#!/bin/bash
# DeePAW Container Welcome Screen

# Rainbow color definitions
RED="\033[91m"
ORANGE="\033[38;5;208m"
YELLOW="\033[93m"
GREEN="\033[92m"
CYAN="\033[96m"
BLUE="\033[94m"
PURPLE="\033[95m"
MAGENTA="\033[35m"
PINK="\033[38;5;213m"

# Other colors
GRAY="\033[90m"
WHITE="\033[97m"
BOLD="\033[1m"
RESET="\033[0m"

clear

echo ""
echo ""

# Top border
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${RESET}"
echo ""

# ASCII art with rainbow colors: D e e e e e P A W
# Using block font for capitals and smaller blocks for lowercase - centered
echo -e "       ${RED}██████╗ ${ORANGE}███${YELLOW}███${GREEN}███${CYAN}███${BLUE}███ ${PURPLE}██████╗  ${MAGENTA}█████╗ ${PINK}██╗    ██╗${RESET}"
echo -e "       ${RED}██╔══██╗${ORANGE}██${YELLOW}███${GREEN}███${CYAN}███${BLUE}███ ${PURPLE}██╔══██╗${MAGENTA}██╔══██╗${PINK}██║    ██║${RESET}"
echo -e "       ${RED}██║  ██║${ORANGE}███${YELLOW}███${GREEN}███${CYAN}███${BLUE}███ ${PURPLE}██████╔╝${MAGENTA}███████║${PINK}██║ █╗ ██║${RESET}"
echo -e "       ${RED}██║  ██║${ORANGE}██${YELLOW}███${GREEN}███${CYAN}███${BLUE}███ ${PURPLE}██╔═══╝ ${MAGENTA}██╔══██║${PINK}██║███╗██║${RESET}"
echo -e "       ${RED}██████╔╝${ORANGE}███${YELLOW}███${GREEN}███${CYAN}███${BLUE}███ ${PURPLE}██║     ${MAGENTA}██║  ██║${PINK}╚███╔███╔╝${RESET}"
echo -e "       ${RED}╚═════╝ ${ORANGE}╚═${YELLOW}═╚═${GREEN}═╚═${CYAN}═╚═${BLUE}═╚═ ${PURPLE}╚═╝     ${MAGENTA}╚═╝  ╚═╝${PINK} ╚══╝╚══╝ ${RESET}"

echo ""
echo -e "${PINK}╚═══════════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# Title
echo -e "${BOLD}${YELLOW}  🚀 DeePAW C++ Inference Engine${RESET}${GRAY} - Encrypted Model Version${RESET}"
echo ""

# Rainbow separator
echo -e "${RED}━${ORANGE}━${YELLOW}━${GREEN}━${CYAN}━${BLUE}━${PURPLE}━${MAGENTA}━${PINK}━${RED}━${ORANGE}━${YELLOW}━${GREEN}━${CYAN}━${BLUE}━${PURPLE}━${MAGENTA}━${PINK}━${RED}━${ORANGE}━${YELLOW}━${GREEN}━${CYAN}━${BLUE}━${PURPLE}━${MAGENTA}━${PINK}━${RED}━${ORANGE}━${YELLOW}━${GREEN}━${CYAN}━${BLUE}━${PURPLE}━${MAGENTA}━${PINK}━${RED}━${ORANGE}━${YELLOW}━${GREEN}━${CYAN}━${BLUE}━${PURPLE}━${MAGENTA}━${PINK}━${RED}━${ORANGE}━${YELLOW}━${GREEN}━${CYAN}━${BLUE}━${PURPLE}━${MAGENTA}━${PINK}━${RED}━${ORANGE}━${YELLOW}━${GREEN}━${CYAN}━${BLUE}━${PURPLE}━${MAGENTA}━${PINK}━${RESET}"
echo ""

# System information
echo -e "${RED}  📦 Version:${RESET}    ${WHITE}v1_cpp${RESET}"
echo -e "${ORANGE}  🐍 Python:${RESET}     ${WHITE}3.12${RESET}"
echo -e "${YELLOW}  🔥 CUDA:${RESET}       ${WHITE}11.8 + cuDNN 8${RESET}"
echo -e "${GREEN}  🔒 Protection:${RESET} ${WHITE}AES-256-GCM Encrypted Models${RESET}"
echo ""

# Quick start section
echo -e "${CYAN}${BOLD}━━━ Quick Start ━━━${RESET}"
echo -e "${GRAY}  python predict_chgcar.py --db tests/hfo2.db --id 1 --device cuda${RESET}"
echo ""

# Environment section
echo -e "${BLUE}${BOLD}━━━ Environment ━━━${RESET}"
echo -e "${GRAY}  PYTHONPATH:  ${WHITE}/app/deepaw${RESET}"
echo -e "${GRAY}  Working Dir: ${WHITE}/app${RESET}"
echo ""

# Bottom rainbow separator
echo -e "${RED}━${ORANGE}━${YELLOW}━${GREEN}━${CYAN}━${BLUE}━${PURPLE}━${MAGENTA}━${PINK}━${RED}━${ORANGE}━${YELLOW}━${GREEN}━${CYAN}━${BLUE}━${PURPLE}━${MAGENTA}━${PINK}━${RED}━${ORANGE}━${YELLOW}━${GREEN}━${CYAN}━${BLUE}━${PURPLE}━${MAGENTA}━${PINK}━${RED}━${ORANGE}━${YELLOW}━${GREEN}━${CYAN}━${BLUE}━${PURPLE}━${MAGENTA}━${PINK}━${RED}━${ORANGE}━${YELLOW}━${GREEN}━${CYAN}━${BLUE}━${PURPLE}━${MAGENTA}━${PINK}━${RED}━${ORANGE}━${YELLOW}━${GREEN}━${CYAN}━${BLUE}━${PURPLE}━${MAGENTA}━${PINK}━${RED}━${ORANGE}━${YELLOW}━${GREEN}━${CYAN}━${BLUE}━${PURPLE}━${MAGENTA}━${PINK}━${RESET}"
echo ""
echo ""
