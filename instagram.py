import requests

class InstagramScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-IG-App-ID": "936619743392459",
        })

    def get_profile(self, username):
        try:
            url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
            r = self.session.get(url, timeout=15)
            if r.status_code == 200:
                user = r.json().get("data", {}).get("user")
                if user:
                    return {
                        "username": user.get("username", ""),
                        "full_name": user.get("full_name", ""),
                        "bio": user.get("biography", ""),
                        "followers": user.get("edge_followed_by", {}).get("count", 0),
                        "following": user.get("edge_follow", {}).get("count", 0),
                        "posts": user.get("edge_owner_to_timeline_media", {}).get("count", 0),
                        "is_verified": user.get("is_verified", False),
                        "is_private": user.get("is_private", False),
                    }
            return {"error": "Profile not found"}
        except Exception as e:
            return {"error": str(e)}
