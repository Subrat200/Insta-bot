import requests
import json
import re
import time
import random
from datetime import datetime
from typing import Optional, Dict, Any


class InstagramScraper:
    """
    Fetches PUBLIC Instagram profile data without login.
    Works only for public accounts.
    """

    BASE_URL = "https://www.instagram.com"
    API_URL = "https://www.instagram.com/api/v1"
    
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "X-IG-App-ID": "936619743392459",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self._init_session()

    def _init_session(self):
        """Initialize session by visiting Instagram homepage."""
        try:
            resp = self.session.get(self.BASE_URL, timeout=10)
            # Extract CSRF token
            csrf = re.search(r'"csrf_token":"([^"]+)"', resp.text)
            if csrf:
                self.session.headers["X-CSRFToken"] = csrf.group(1)
        except Exception:
            pass

    def _delay(self):
        """Random polite delay to avoid rate limiting."""
        time.sleep(random.uniform(0.5, 1.5))

    def get_profile(self, username: str) -> Dict[str, Any]:
        """Fetch public profile info for a username."""
        self._delay()
        try:
            # Method 1: Use the public web profile API
            url = f"{self.BASE_URL}/api/v1/users/web_profile_info/?username={username}"
            resp = self.session.get(url, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                user = data.get("data", {}).get("user")
                if user:
                    return self._parse_user(user)

            # Method 2: Fallback to JSON endpoint
            url2 = f"{self.BASE_URL}/{username}/?__a=1&__d=dis"
            resp2 = self.session.get(url2, timeout=15)
            if resp2.status_code == 200:
                data2 = resp2.json()
                user2 = (
                    data2.get("graphql", {}).get("user") or
                    data2.get("data", {}).get("user")
                )
                if user2:
                    return self._parse_user(user2)

            if resp.status_code == 404:
                return {"error": f"User '@{username}' not found"}
            if resp.status_code == 429:
                return {"error": "Rate limited. Please wait a minute and try again."}
            if resp.status_code == 401:
                return {"error": "This account is private or Instagram requires login."}

            return {"error": f"Could not fetch profile (HTTP {resp.status_code})"}

        except requests.exceptions.Timeout:
            return {"error": "Request timed out. Try again."}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error. Check your internet."}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def _parse_user(self, user: dict) -> dict:
        """Normalize user data from various API response formats."""
        followers = (
            user.get("edge_followed_by", {}).get("count") or
            user.get("follower_count") or 0
        )
        following = (
            user.get("edge_follow", {}).get("count") or
            user.get("following_count") or 0
        )
        posts = (
            user.get("edge_owner_to_timeline_media", {}).get("count") or
            user.get("media_count") or 0
        )
        return {
            "username": user.get("username", ""),
            "full_name": user.get("full_name", ""),
            "bio": user.get("biography", "") or user.get("bio", ""),
            "followers": int(followers),
            "following": int(following),
            "posts": int(posts),
            "is_verified": user.get("is_verified", False),
            "is_private": user.get("is_private", False),
            "profile_pic_url": user.get("profile_pic_url_hd") or user.get("profile_pic_url", ""),
            "external_url": user.get("external_url", ""),
            "user_id": user.get("id", ""),
        }

    def get_posts(self, username: str) -> Dict[str, Any]:
        """Fetch recent public posts for a username."""
        self._delay()
        try:
            # First get profile to check if public
            profile = self.get_profile(username)
            if profile.get("error"):
                return profile
            if profile.get("is_private"):
                return {"error": "This account is private. Cannot fetch posts."}

            url = f"{self.BASE_URL}/api/v1/feed/user/{username}/username/?count=12"
            resp = self.session.get(url, timeout=15)

            posts = []
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                for item in items:
                    posts.append(self._parse_post(item))
            else:
                # Fallback: scrape from web profile
                url2 = f"{self.BASE_URL}/{username}/?__a=1&__d=dis"
                resp2 = self.session.get(url2, timeout=15)
                if resp2.status_code == 200:
                    data2 = resp2.json()
                    user = (
                        data2.get("graphql", {}).get("user") or
                        data2.get("data", {}).get("user", {})
                    )
                    edges = user.get("edge_owner_to_timeline_media", {}).get("edges", [])
                    for edge in edges[:12]:
                        node = edge.get("node", {})
                        posts.append(self._parse_graphql_post(node))

            return {"posts": posts, "username": username}

        except Exception as e:
            return {"error": str(e)}

    def _parse_post(self, item: dict) -> dict:
        """Parse post from API v1 format."""
        media_type = item.get("media_type", 1)
        taken_at = item.get("taken_at", 0)
        date_str = datetime.fromtimestamp(taken_at).strftime("%b %d, %Y") if taken_at else "N/A"

        thumbnail = None
        if item.get("image_versions2"):
            candidates = item["image_versions2"].get("candidates", [])
            if candidates:
                thumbnail = candidates[0].get("url")
        elif item.get("carousel_media"):
            first = item["carousel_media"][0]
            candidates = first.get("image_versions2", {}).get("candidates", [])
            if candidates:
                thumbnail = candidates[0].get("url")

        caption_text = ""
        caption = item.get("caption")
        if caption and isinstance(caption, dict):
            caption_text = caption.get("text", "")

        return {
            "id": item.get("id", ""),
            "likes": item.get("like_count", 0),
            "comments": item.get("comment_count", 0),
            "caption": caption_text,
            "date": date_str,
            "thumbnail": thumbnail,
            "type": "video" if media_type == 2 else "image",
            "url": f"https://www.instagram.com/p/{item.get('code', '')}/" if item.get("code") else "",
        }

    def _parse_graphql_post(self, node: dict) -> dict:
        """Parse post from GraphQL format."""
        taken_at = node.get("taken_at_timestamp", 0)
        date_str = datetime.fromtimestamp(taken_at).strftime("%b %d, %Y") if taken_at else "N/A"

        thumbnail = node.get("thumbnail_src") or node.get("display_url", "")
        caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
        caption = caption_edges[0]["node"]["text"] if caption_edges else ""

        return {
            "id": node.get("id", ""),
            "likes": node.get("edge_liked_by", {}).get("count", 0),
            "comments": node.get("edge_media_to_comment", {}).get("count", 0),
            "caption": caption,
            "date": date_str,
            "thumbnail": thumbnail,
            "type": "video" if node.get("is_video") else "image",
            "url": f"https://www.instagram.com/p/{node.get('shortcode', '')}/",
        }

    def get_stories(self, username: str) -> Dict[str, Any]:
        """
        Attempt to fetch public stories.
        Note: Stories require login for most accounts.
        Returns empty list for accounts without accessible stories.
        """
        self._delay()
        try:
            profile = self.get_profile(username)
            if profile.get("error"):
                return profile
            if profile.get("is_private"):
                return {"error": "This is a private account. Stories are not accessible."}

            user_id = profile.get("user_id")
            if not user_id:
                return {"stories": [], "note": "Could not retrieve story data without authentication."}

            url = f"{self.API_URL}/feed/reels_media/?reel_ids={user_id}"
            resp = self.session.get(url, timeout=15)

            stories = []
            if resp.status_code == 200:
                data = resp.json()
                reels = data.get("reels", {})
                reel = reels.get(str(user_id), {})
                items = reel.get("items", [])
                for item in items:
                    stories.append(self._parse_story(item))

            if not stories:
                return {
                    "stories": [],
                    "note": (
                        "No active stories found. "
                        "Stories may require authentication to view, "
                        "or this user has no active stories."
                    )
                }

            return {"stories": stories, "username": username}

        except Exception as e:
            return {"error": str(e)}

    def _parse_story(self, item: dict) -> dict:
        """Parse a story item."""
        taken_at = item.get("taken_at", 0)
        date_str = datetime.fromtimestamp(taken_at).strftime("%b %d, %Y %H:%M") if taken_at else "N/A"

        media_type = item.get("media_type", 1)
        thumbnail = None
        video_url = None

        if media_type == 2:  # Video
            video_versions = item.get("video_versions", [])
            if video_versions:
                video_url = video_versions[0].get("url")
            candidates = item.get("image_versions2", {}).get("candidates", [])
            if candidates:
                thumbnail = candidates[0].get("url")
        else:  # Image
            candidates = item.get("image_versions2", {}).get("candidates", [])
            if candidates:
                thumbnail = candidates[0].get("url")

        return {
            "id": item.get("id", ""),
            "type": "video" if media_type == 2 else "image",
            "thumbnail": thumbnail,
            "url": video_url,
            "date": date_str,
            "duration": item.get("video_duration"),
        }
