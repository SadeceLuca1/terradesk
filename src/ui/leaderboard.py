"""
TerraDesk – Online Leaderboard
Tracks installs / play sessions via a free JSON bin.
Data is stored at jsonbin.io (free, no auth needed for read).
Players appear on the leaderboard just by playing the game.
"""
from __future__ import annotations
import os, json, threading, socket, hashlib, platform, time
from typing import List, Dict, Optional

# Free public bin on jsonbin.io – replace BIN_ID after creating one at jsonbin.io
# To create: POST to https://api.jsonbin.io/v3/b with {"leaderboard":[]}
# and copy the bin id from the response.
LEADERBOARD_URL = "https://api.jsonbin.io/v3/b/6744000000000000000000/latest"
LEADERBOARD_POST = "https://api.jsonbin.io/v3/b/6744000000000000000000"

# Fallback: use a simple free pastebin-style API
# We use https://jsonblob.com (completely free, no signup)
BLOB_API = "https://jsonblob.com/api/jsonBlob"

# Local cache
CACHE_FILE = os.path.join(os.path.expanduser("~"), ".terradesk", "leaderboard_cache.json")
PLAYER_FILE = os.path.join(os.path.expanduser("~"), ".terradesk", "player_id.json")

_leaderboard_cache: Optional[List[Dict]] = None
_my_entry: Optional[Dict] = None


def _get_player_id() -> Dict:
    """Get or create a persistent player identity."""
    global _my_entry
    os.makedirs(os.path.dirname(PLAYER_FILE), exist_ok=True)

    if os.path.exists(PLAYER_FILE):
        try:
            with open(PLAYER_FILE, "r") as f:
                data = json.load(f)
                _my_entry = data
                return data
        except Exception:
            pass

    # Create new identity
    hostname = socket.gethostname()
    user = os.environ.get("USERNAME", os.environ.get("USER", "player"))
    # Generate a unique but anonymous ID
    raw = f"{hostname}-{user}-{time.time()}"
    uid = hashlib.md5(raw.encode()).hexdigest()[:8].upper()

    # Pick a fun village name
    import random
    adjectives = ["Brave", "Swift", "Wise", "Green", "Golden", "Silver", "Mystic",
                  "Ancient", "Mighty", "Happy", "Lucky", "Jolly", "Noble", "Proud"]
    nouns = ["Village", "Town", "Hamlet", "Keep", "Realm", "Vale", "Haven",
             "Fort", "Hold", "Shire", "Grove", "Field", "Glen", "Moor"]
    display_name = f"{random.choice(adjectives)} {random.choice(nouns)} #{uid[:4]}"

    entry = {
        "id": uid,
        "name": display_name,
        "installs": 1,
        "play_minutes": 0,
        "first_seen": time.strftime("%Y-%m-%d"),
        "last_seen": time.strftime("%Y-%m-%d"),
        "platform": platform.system(),
    }
    _my_entry = entry
    try:
        with open(PLAYER_FILE, "w") as f:
            json.dump(entry, f, indent=2)
    except Exception:
        pass
    return entry


def _load_cache() -> List[Dict]:
    """Load cached leaderboard from disk."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_cache(data: List[Dict]):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def _fetch_leaderboard_online() -> Optional[List[Dict]]:
    """Try to fetch leaderboard from GitHub Gist (free, no auth needed)."""
    try:
        import urllib.request, urllib.error
        # We store leaderboard in a public GitHub Gist
        # Gist ID is set when first created; fall back to local-only if not set
        gist_id = _get_gist_id()
        if not gist_id:
            return None
        url = f"https://gist.githubusercontent.com/SadeceLuca1/{gist_id}/raw/leaderboard.json"
        req = urllib.request.Request(url, headers={"User-Agent": "TerraDesk/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def _get_gist_id() -> Optional[str]:
    """Read the gist ID from local config (set once after first upload)."""
    cfg = os.path.join(os.path.expanduser("~"), ".terradesk", "config.json")
    if os.path.exists(cfg):
        try:
            with open(cfg) as f:
                return json.load(f).get("leaderboard_gist_id")
        except Exception:
            pass
    return None


def _update_local_leaderboard(player: Dict, board: List[Dict]) -> List[Dict]:
    """Merge player entry into leaderboard list."""
    for i, entry in enumerate(board):
        if entry.get("id") == player["id"]:
            # Update existing
            board[i]["play_minutes"] = entry.get("play_minutes", 0) + player.get("play_minutes", 0)
            board[i]["last_seen"] = time.strftime("%Y-%m-%d")
            board[i]["name"] = player["name"]
            return board
    # New player
    board.append(player.copy())
    return board


def _update_play_time(minutes: int):
    """Update the player's accumulated play time."""
    if _my_entry and os.path.exists(PLAYER_FILE):
        try:
            with open(PLAYER_FILE) as f:
                data = json.load(f)
            data["play_minutes"] = data.get("play_minutes", 0) + minutes
            data["last_seen"] = time.strftime("%Y-%m-%d")
            _my_entry.update(data)
            with open(PLAYER_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass


# ── Public API ─────────────────────────────────────────────────────────────────

class Leaderboard:
    """Manages the online/offline leaderboard display."""

    def __init__(self):
        self.entries: List[Dict] = []
        self.my_rank: int = 0
        self.my_entry: Optional[Dict] = None
        self._loaded = False
        self._session_start = time.time()

        # Init player identity (non-blocking)
        self.my_entry = _get_player_id()
        # Load from cache immediately for instant display
        self.entries = _load_cache()
        # Fetch online in background
        threading.Thread(target=self._background_refresh, daemon=True).start()

    def _background_refresh(self):
        """Fetch leaderboard online and merge player entry."""
        online = _fetch_leaderboard_online()
        if online is not None:
            board = online
        else:
            board = self.entries[:]

        if self.my_entry:
            board = _update_local_leaderboard(self.my_entry, board)

        # Sort by play_minutes desc
        board.sort(key=lambda e: e.get("play_minutes", 0), reverse=True)
        self.entries = board
        _save_cache(board)
        self._loaded = True

        # Find own rank
        my_id = self.my_entry.get("id") if self.my_entry else None
        for i, e in enumerate(board):
            if e.get("id") == my_id:
                self.my_rank = i + 1
                break

    def save_session(self):
        """Call on game exit to record play time."""
        minutes = int((time.time() - self._session_start) / 60)
        if minutes > 0 and self.my_entry:
            _update_play_time(minutes)

    @property
    def top10(self) -> List[Dict]:
        return self.entries[:10]

    @property
    def player_name(self) -> str:
        return self.my_entry.get("name", "Unknown") if self.my_entry else "Unknown"

    @property
    def player_minutes(self) -> int:
        return self.my_entry.get("play_minutes", 0) if self.my_entry else 0
