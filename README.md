# 🏗️ BuildSA

A South African community platform for builders, contractors, and homeowners.

**🌐 Live Demo:** https://buildsa-d0i1.onrender.com

## Features

- Public feed (questions, projects, ads, materials)
- Private one-on-one messaging
- Crowd-sourced material prices by province
- Follow other builders + verified badges
- Photo and video uploads
- AI assistant with SA material prices
- Admin approval workflow

## Tech Stack

Python 3 · Flask · SQLAlchemy · MySQL (Aiven Cloud) · Groq (Llama 3.1) · Bootstrap 5 · Render · UptimeRobot

## Local Setup

    git clone https://github.com/Thapelo-Makama/buildsa.git
    cd buildsa
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python init_db.py
    python run.py

Open http://localhost:5000

**Admin:** admin / Admin@2024!
**Demo:** builder1 / Builder@2024!

## License

MIT © Thapelo Makama

## Author

**Thapelo Makama**
- GitHub: [@Thapelo-Makama](https://github.com/Thapelo-Makama)
- Live: [buildsa-d0i1.onrender.com](https://buildsa-d0i1.onrender.com)
