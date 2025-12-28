# Auto News Publisher AI Automation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)

## 🚀 Project Overview

Auto News Publisher AI Automation is a professional, production-ready solution for fully automated news content generation and publishing. It leverages AI (OpenAI, Anthropic) to write high-quality articles, fetches trending news, scrapes relevant images, and publishes to Blogger and Facebook — all with minimal human intervention.

### ✨ Features
- 🔥 Fetches trending news from multiple sources (NewsAPI, Google News, Reddit)
- 🤖 AI-powered article writing (OpenAI GPT, Anthropic Claude)
- 🖼️ Automatic image scraping and optimization
- 📢 Publishes to Blogger and Facebook Pages
- 🕒 Fully automated, scheduled posting
- 🛡️ Secure: No secrets or API keys in the repo
- 📦 Modular, extensible, and easy to customize

## 📸 Demo
![Auto News Publisher Demo](https://user-images.githubusercontent.com/your-github-username/demo-gif-or-image.gif)

## 🛠️ Quick Start
1. **Clone the repository:**
	```bash
	git clone https://github.com/pikumandal2005/auto-news-publisher-ai-automation.git
	cd auto-news-publisher-ai-automation
	```
2. **Install dependencies:**
	```bash
	pip install -r requirements.txt
	```
3. **Configure your API keys:**
	- Copy `config.example.json` to `config.json` and fill in your keys.
	- Copy `client_secret.example.json` to `client_secret.json` and add your Google OAuth credentials.
4. **Run the automation:**
	```bash
	python auto_post_1min.py
	# or
	python auto_post_dual_platform.py
	```

## 📂 Project Structure
```
├── auto_post_1min.py           # Blogger auto-post script
├── auto_post_dual_platform.py  # Blogger + Facebook auto-post script
├── main.py                     # Main automation workflow
├── modules/                    # All core modules (news, AI, images, publishers)
├── config.example.json         # Example config (no secrets)
├── client_secret.example.json  # Example Google OAuth config
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
```

## 🤝 Contributing
We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md).

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

> **Why Recruiters Love This Project:**
> - Demonstrates real-world automation, AI integration, and API skills
> - Clean, modular, and production-ready code
> - Secure handling of credentials and configs
> - Professional documentation and open-source best practices

---

For questions or collaboration, connect via [GitHub Issues](https://github.com/pikumandal2005/auto-news-publisher-ai-automation/issues).
