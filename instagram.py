import requests

class InstagramScraper:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers["User-Agent"] = "Mozilla/5.0"
        self.s.headers["X-IG-App-ID"] = "936619743392459"

    def get_profile(self, username):
        try:
            r = self.s.get(
                f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
                timeout=15
            )
            u = r.json().get("data", {}).get("user", {})
            if not u:
                return {"error": "Profile not found"}
            return {
                "username": u.get("username", ""),
                "full_name": u.get("full_name", ""),
                "bio": u.get("biography", ""),
                "followers": u.get("edge_followed_by", {}).get("count", 0),
                "following": u.get("edge_follow", {}).get("count", 0),
                "posts": u.get("edge_owner_to_timeline_media", {}).get("count", 0),
                "is_verified": u.get("is_verified", False),
                "is_private": u.get("is_private", False),
            }
        except Exception as e:
            return {"error": str(e)}
