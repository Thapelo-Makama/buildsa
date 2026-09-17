from flask import current_app
from difflib import get_close_matches

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class AIAssistant:
    def __init__(self):
        self.client = None
        self.model = None

    def initialize(self):
        api_key = current_app.config.get('GROQ_API_KEY')
        self.model = current_app.config.get('AI_MODEL', 'llama-3.1-8b-instant')
        if api_key and GROQ_AVAILABLE:
            try:
                self.client = Groq(api_key=api_key)
            except Exception as e:
                current_app.logger.warning(f"Groq init failed: {e}")
                self.client = None
        else:
            self.client = None

    def generate_response(self, msg, user_context=None, page_url=None, user_id=None):
        msg = msg.strip()
        if self.client:
            try:
                system = (
                    "You are BuildSA's AI assistant for South African builders. "
                    "Help with material prices (cement, bricks, sand, tiles), "
                    "how many bricks/cement bags for typical projects, "
                    "NHBRC guidelines, house plan basics, and using BuildSA. "
                    "Quote prices in ZAR (R). Keep answers under 200 words."
                )
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": msg},
                    ],
                    temperature=0.6,
                    max_tokens=400,
                )
                return completion.choices[0].message.content
            except Exception as e:
                current_app.logger.error(f"Groq error: {e}")
        return self._keyword_fallback(msg)

    def _keyword_fallback(self, msg):
        m = msg.lower()
        topics = {
            'bricks': (['brick', 'briks'],
                "Bricks in SA (2026): Common clay R2.50-R4.50, Face brick R4-R7, "
                "Cement stock R3-R5 each. Rough rule: 50 bricks per m2. "
                "A 100m2 house ~ 25,000 bricks."),
            'cement': (['cement', 'cemnt', 'ppc', 'sement'],
                "Cement prices: PPC 50kg R95-R120, AfriSam R90-R115, "
                "Sephaku R85-R110. Foundation (25m2 slab): ~80 bags. "
                "Brickwork: 1 bag per 500 bricks. Plaster: 1 bag per 4m2."),
            'sand': (['sand', 'plaster sand', 'river sand'],
                "Sand: Building sand R300-R450 per m3, Plaster R450-R600, "
                "River R500-R700. Delivery adds R150-R400."),
            'house plan': (['house plan', 'plan', 'blueprint'],
                "House plans in SA: Single-storey 100m2 R8k-R20k, "
                "Double-storey 200m2 R20k-R45k. Must comply with SANS 10400 "
                "and be submitted for municipal approval."),
            'cost': (['cost', 'price', 'how much', 'budget'],
                "Building costs in SA (2026): RDP style R4,500/m2, "
                "Standard house R7,500-R12,000/m2, Luxury R15,000-R30,000/m2. "
                "100m2 basic house = R750k-R1.2M."),
            'tiles': (['tile', 'tiling'],
                "Tiles: Ceramic R130-R250/m2, Porcelain R250-R500/m2, "
                "Wall R80-R200/m2. Buy 10% extra for cuts."),
            'roof': (['roof', 'roofing', 'ibr', 'chromadek'],
                "Roofing: IBR R180-R280/m2, Concrete tiles R250-R450/m2, "
                "Clay tiles R350-R600/m2. Add timber trusses R180-R280/m2."),
            'platform': (['platform', 'what is', 'how to use', 'buildsa'],
                "Welcome to BuildSA! Post questions, projects, ads; "
                "message builders privately; share material prices; "
                "follow other builders; ask me anything about SA building."),
            'register': (['register', 'sign up', 'create account'],
                "To register: click 'Register', fill details, wait for "
                "admin approval, then you can post and message."),
            'post': (['post', 'share', 'publish'],
                "To post: click 'New Post', choose category, write content, "
                "add photo/video (optional), click 'Post'."),
        }
        for key, (kw_list, resp) in topics.items():
            for kw in kw_list:
                if kw in m:
                    return resp
        all_kw = [k for v in topics.values() for k in v[0]]
        matches = get_close_matches(m, all_kw, n=1, cutoff=0.55)
        if matches:
            for key, (kw_list, resp) in topics.items():
                if matches[0] in kw_list:
                    return resp
        return ("Hi! I'm the BuildSA assistant. Ask me about brick prices, "
                "cement bags needed, house plans, building costs per m2, "
                "or how to use BuildSA.")

    def get_suggestion_buttons(self, page_url):
        mapping = {
            '/': ["Brick prices?", "Cement prices?", "How to build?"],
            '/feed': ["How to post?", "House plans?", "Building costs?"],
            '/materials': ["Cement prices", "Brick prices", "Sand prices"],
        }
        for path, b in mapping.items():
            if path in page_url:
                return b
        return ["Brick prices?", "Cement prices?", "How to use BuildSA?"]
