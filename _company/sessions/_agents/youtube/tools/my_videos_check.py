#!/usr/bin/env python3
"""My Videos Check — pulls your own channel's recent uploads, computes a
view-count baseline (median of last N), and flags which videos are above /
below the line. Outputs a short report. Optionally pings Telegram.

Reads YOUTUBE_API_KEY + MY_CHANNEL_HANDLE/ID from youtube_account.json.
Reads LOOKBACK_DAYS / TOP_N from my_videos_check.json."""
import os, json, sys, time, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ACCOUNT = os.path.join(HERE, "youtube_account.json")
CONFIG  = os.path.join(HERE, "my_videos_check.json")
REPORT  = os.path.join(HERE, "my_videos_check_report.md")

def _load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def _resolve_channel_id(youtube, handle, channel_id):
    if channel_id:
        return channel_id
    if not handle:
        return None
    h = handle if handle.startswith("@") else "@" + handle
    try:
        r = youtube.channels().list(part="id", forHandle=h).execute()
        items = r.get("items", [])
        if items:
            return items[0]["id"]
    except Exception as e:
        print(f"⚠️  채널 ID 조회 실패: {e}")
    return None

def _push_telegram(account, text):
    token = (account.get("TELEGRAM_BOT_TOKEN") or "").strip()
    chat  = (account.get("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat:
        return
    try:
        import requests
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": text, "parse_mode": "Markdown"},
            timeout=10,
        )
        print("📨 텔레그램으로 보고 전송")
    except Exception as e:
        print(f"⚠️  텔레그램 전송 실패: {e}")

def main():
    if not os.path.exists(ACCOUNT):
        print("❌ youtube_account.json이 없어요. 같은 폴더에서 youtube_account 도구를 먼저 실행/설정하세요.")
        sys.exit(1)
    acct = _load(ACCOUNT)
    cfg  = _load(CONFIG) if os.path.exists(CONFIG) else {}
    api_key = (acct.get("YOUTUBE_API_KEY") or "").strip()
    handle  = (acct.get("MY_CHANNEL_HANDLE") or "").strip()
    chan_id = (acct.get("MY_CHANNEL_ID") or "").strip()
    if not api_key:
        print("❌ YOUTUBE_API_KEY가 비어있어요. youtube_account.json에 채워주세요.")
        sys.exit(1)
    if not (handle or chan_id):
        print("❌ MY_CHANNEL_HANDLE 또는 MY_CHANNEL_ID 중 하나는 채워야 해요.")
        sys.exit(1)
    lookback = int(cfg.get("LOOKBACK_DAYS", 30))
    top_n    = int(cfg.get("TOP_N", 10))

    try:
        from googleapiclient.discovery import build
    except ImportError:
        print("❌ google-api-python-client 미설치. pip install google-api-python-client requests")
        sys.exit(1)
    youtube = build("youtube", "v3", developerKey=api_key)

    cid = _resolve_channel_id(youtube, handle, chan_id)
    if not cid:
        print("❌ 채널 ID를 찾지 못했어요. youtube_account.json의 핸들/ID 확인.")
        sys.exit(1)

    # uploads playlist ID 구하기 (1 unit 쿼타)
    uploads_playlist = ""
    try:
        ch_res = youtube.channels().list(part="contentDetails", id=cid).execute()
        if ch_res.get("items"):
            uploads_playlist = ch_res["items"][0].get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads", "")
    except Exception as e:
        print(f"⚠️  채널 메타 조회 실패: {e}")

    print(f"🎬 [내 영상 체크] 채널 {handle or cid} 최근 {top_n}개 분석 중...")
    vids = []
    if uploads_playlist:
        try:
            pi_resp = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist,
                maxResults=max(50, top_n)
            ).execute()
            
            limit_dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=lookback)
            raw_vids = []
            for it in pi_resp.get("items", []):
                snippet = it.get("snippet", {})
                vid = snippet.get("resourceId", {}).get("videoId", "")
                title = snippet.get("title", "")
                pub_at = snippet.get("publishedAt", "")
                raw_vids.append((vid, title, pub_at))
                
                try:
                    pub_dt = datetime.datetime.fromisoformat(pub_at.replace("Z", "+00:00"))
                    if pub_dt >= limit_dt:
                        vids.append((vid, title, pub_at))
                except Exception:
                    vids.append((vid, title, pub_at))
            
            if not vids:
                vids = raw_vids[:top_n]
            else:
                vids = vids[:top_n]
        except Exception as e:
            print(f"⚠️  플레이리스트 조회 실패: {e}")

    stats = youtube.videos().list(part="statistics", id=",".join(v[0] for v in vids)).execute()
    sm = {it["id"]: it["statistics"] for it in stats.get("items", [])}
    rows = []
    for vid, title, pub in vids:
        s = sm.get(vid, {})
        views = int(s.get("viewCount", 0))
        likes = int(s.get("likeCount", 0))
        comments = int(s.get("commentCount", 0))
        rows.append({"id": vid, "title": title, "pub": pub[:10], "views": views, "likes": likes, "comments": comments})

    rows.sort(key=lambda r: r["views"], reverse=True)
    views_list = sorted([r["views"] for r in rows])
    median = views_list[len(views_list)//2] if views_list else 0

    print("\n" + "="*60)
    print(f"중간값(median) 조회수: {median:,}")
    print("="*60)
    for r in rows:
        marker = "🔥" if r["views"] >= median * 1.5 else ("👍" if r["views"] >= median else "🥶")
        print(f"{marker} {r['views']:>7,}회 · {r['pub']} · {r['title'][:60]}")
        print(f"   https://youtu.be/{r['id']}")

    above = [r for r in rows if r["views"] >= median * 1.5]
    below = [r for r in rows if r["views"] < median * 0.5]

    summary_lines = [
        f"# 🎬 내 채널 체크 — {time.strftime('%Y-%m-%d %H:%M')}",
        f"채널: {handle or cid} · 최근 {lookback}일 · 영상 {len(rows)}개",
        f"조회수 중간값: **{median:,}**",
        "",
        f"## 🔥 떡상 (중간값×1.5 이상) — {len(above)}개",
    ]
    for r in above[:5]:
        summary_lines.append(f"- {r['views']:,}회 · {r['title']}")
    summary_lines.append(f"\n## 🥶 부진 (중간값×0.5 미만) — {len(below)}개")
    for r in below[:5]:
        summary_lines.append(f"- {r['views']:,}회 · {r['title']}")
    summary_lines.append("\n## 다음 액션 (제안)")
    if above:
        summary_lines.append(f"- 🔥 떡상한 영상의 후크/제목 패턴을 트렌드 스나이퍼 결과와 교차 분석")
    if below:
        summary_lines.append(f"- 🥶 부진 영상은 썸네일 A/B 또는 제목 리네이밍 후보")
    summary_lines.append("- 댓글 수집기를 돌려서 시청자 반응 키워드 확인")
    summary = "\n".join(summary_lines)

    with open(REPORT, "a", encoding="utf-8") as f:
        f.write("\n\n" + summary + "\n\n---\n")
    print(f"\n✅ 보고서: {REPORT}")
    _push_telegram(acct, summary)

if __name__ == "__main__":
    main()
