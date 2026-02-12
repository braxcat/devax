"""
Slack Bot Token API client — stdlib only (no dependencies).

Uses Bot User OAuth Token (xoxb-...) for:
- Posting messages to channels
- Creating channels
- Joining channels
- Listing channels
"""

import json
import time
import urllib.request
import urllib.error
import os


def _get_token():
    """Get SLACK_BOT_TOKEN from environment."""
    token = os.environ.get("SLACK_BOT_TOKEN", "")
    if not token:
        raise EnvironmentError(
            "SLACK_BOT_TOKEN not set. Export your Bot User OAuth Token:\n"
            "  export SLACK_BOT_TOKEN='xoxb-...'"
        )
    if not token.startswith("xoxb-"):
        raise ValueError(
            f"SLACK_BOT_TOKEN should start with 'xoxb-', got '{token[:8]}...'"
        )
    return token


def slack_api(token, method, payload):
    """POST to Slack Web API. Returns parsed JSON response."""
    url = f"https://slack.com/api/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return {"ok": False, "error": f"HTTP {e.code}", "body": body}
    except urllib.error.URLError as e:
        return {"ok": False, "error": str(e.reason)}


def list_channels(token):
    """List all public channels. Returns {name: channel_id} map."""
    channels = {}
    cursor = None
    while True:
        payload = {"types": "public_channel", "limit": 200}
        if cursor:
            payload["cursor"] = cursor
        resp = slack_api(token, "conversations.list", payload)
        if not resp.get("ok"):
            raise RuntimeError(f"conversations.list failed: {resp.get('error')}")
        for ch in resp.get("channels", []):
            channels[ch["name"]] = ch["id"]
        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
    return channels


def create_channel(token, name):
    """Create a public channel. Returns channel_id. Handles name_taken."""
    resp = slack_api(token, "conversations.create", {"name": name, "is_private": False})
    if resp.get("ok"):
        return resp["channel"]["id"]
    if resp.get("error") == "name_taken":
        # Channel exists — find its ID
        existing = list_channels(token)
        if name in existing:
            return existing[name]
        raise RuntimeError(f"Channel '{name}' exists but not found in list")
    raise RuntimeError(f"conversations.create failed: {resp.get('error')}")


def join_channel(token, channel_id):
    """Join a channel."""
    resp = slack_api(token, "conversations.join", {"channel": channel_id})
    if not resp.get("ok") and resp.get("error") != "already_in_channel":
        raise RuntimeError(f"conversations.join failed: {resp.get('error')}")


def post_message(token, channel_id, blocks, text=""):
    """Post a Block Kit message to a channel."""
    payload = {
        "channel": channel_id,
        "blocks": blocks,
        "text": text or "Dev update",
    }
    resp = slack_api(token, "chat.postMessage", payload)
    if not resp.get("ok"):
        raise RuntimeError(f"chat.postMessage failed: {resp.get('error')}")
    return resp


def ensure_channels(token, channel_names):
    """Create channels if they don't exist, join them. Returns {name: channel_id}."""
    existing = list_channels(token)
    result = {}
    for name in channel_names:
        if name in existing:
            ch_id = existing[name]
        else:
            print(f"  Creating #{name}...")
            ch_id = create_channel(token, name)
        join_channel(token, ch_id)
        result[name] = ch_id
        print(f"  #{name} -> {ch_id}")
    return result


def delete_message(token, channel_id, ts):
    """Delete a message by timestamp. Bot can only delete its own messages."""
    resp = slack_api(token, "chat.delete", {"channel": channel_id, "ts": ts})
    if not resp.get("ok"):
        raise RuntimeError(f"chat.delete failed: {resp.get('error')}")
    return resp


def get_bot_messages(token, channel_id, limit=20):
    """Get recent bot messages from a channel. Returns list of {ts, text, blocks}."""
    resp = slack_api(token, "conversations.history", {"channel": channel_id, "limit": limit})
    if not resp.get("ok"):
        raise RuntimeError(f"conversations.history failed: {resp.get('error')}")
    messages = []
    for m in resp.get("messages", []):
        if m.get("bot_id") or m.get("subtype") == "bot_message":
            messages.append({
                "ts": m["ts"],
                "text": m.get("text", ""),
            })
    return messages


def delete_bot_messages(token, channel_id, count):
    """Delete the last N bot messages from a channel."""
    messages = get_bot_messages(token, channel_id, limit=count + 5)
    deleted = 0
    for m in messages:
        if deleted >= count:
            break
        try:
            delete_message(token, channel_id, m["ts"])
            deleted += 1
            print(f"  Deleted message {m['ts']}")
        except RuntimeError as e:
            print(f"  Failed to delete {m['ts']}: {e}")
    return deleted


def delete_all_bot_messages(token, channel_id):
    """Delete ALL bot messages from a channel using cursor pagination.

    Handles rate limiting (429) with retry and skips messages posted by
    other integrations (cant_delete_message).
    """
    deleted = 0
    skipped = 0
    cursor = None
    while True:
        payload = {"channel": channel_id, "limit": 100}
        if cursor:
            payload["cursor"] = cursor
        resp = slack_api(token, "conversations.history", payload)
        if not resp.get("ok"):
            raise RuntimeError(f"conversations.history failed: {resp.get('error')}")

        bot_messages = [
            m for m in resp.get("messages", [])
            if m.get("bot_id") or m.get("subtype") == "bot_message"
        ]

        if not bot_messages and not resp.get("has_more"):
            break

        for m in bot_messages:
            try:
                delete_message(token, channel_id, m["ts"])
                deleted += 1
                time.sleep(0.3)  # rate limit: ~3 deletes/sec
            except RuntimeError as e:
                err_str = str(e)
                if "429" in err_str:
                    time.sleep(3)  # back off on rate limit
                    try:
                        delete_message(token, channel_id, m["ts"])
                        deleted += 1
                    except RuntimeError:
                        skipped += 1
                elif "cant_delete_message" in err_str:
                    skipped += 1  # webhook message, can't delete
                else:
                    skipped += 1

        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    return deleted
