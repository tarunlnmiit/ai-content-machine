---
title: "You Don't Need Mastodon.py to Automate Toots — Just `requests` and 40 Lines"
type: blog
niche: data_science_tech
date: 2026-07-16
week: 2026-W29
slug: building-a-mastodon-automation-bot-using-python-and-streamli
tags: [content/blog, niche/data_science_tech, week/2026-W29]
---
# You Don't Need Mastodon.py to Automate Toots — Just `requests` and 40 Lines

I installed `Mastodon.py`, imported it, and then spent twenty minutes reading its docs to figure out how to attach one image to one post. That's when I closed the tab and opened the network inspector instead — because Mastodon's API is only two HTTP endpoints, and I'd been about to pull in a 4,000-line dependency to call them.

Here's the thing most tutorials skip: posting to Mastodon is `POST /api/v1/media` followed by `POST /api/v1/statuses`. That's the whole surface area for a bot that posts text and pictures. A wrapper library exists, and it's genuinely good if you want to read timelines, follow users, and stream notifications. But if all you want is a small tool that fires off a toot with an image, the library is weight you carry for features you'll never call. Every dependency you add is a thing that can break, deprecate, or change its API on a Tuesday — and the two endpoints you need have been stable for years.

![laptop screen showing python code in a terminal editor](/content/blogs/2026-W29/2026-07-16_data_science_tech_building-a-mastodon-automation-bot-using-python-and-streamli_images/01_hook_laptop-screen-showing-python-code-in-a-terminal-ed.jpg)
*laptop screen showing python code in a terminal editor — Photo by [Mathews Jumba](https://www.pexels.com/photo/black-screen-of-a-monitor-5242012/) on Pexels*

## The Two Endpoints That Are the Entire Job

Mastodon's REST API is well-documented and refreshingly boring, which is the highest compliment I can pay an API. For a posting bot, you touch exactly two routes.

The first is `POST /api/v1/media`. You hand it a file, it stores the image and hands you back a media ID — a string like `"109834..."`. The image isn't posted yet; it's parked on the server, waiting to be attached to something.

The second is `POST /api/v1/statuses`. This is the actual toot. You send it a `status` field with your text, and optionally a `media_ids[]` field listing the IDs you got back from the first call. Send it, and the post goes live.

Both are authenticated the same way: a bearer token in the `Authorization` header. No OAuth dance at runtime, no session juggling, no cookies. You generate one token once, from your account settings, and every request carries it.

Before any code, you need that token. Log into your instance (mine is `me.dm`, Medium's Mastodon instance), go to **Preferences → Development → New Application**, and check two scopes: `write:statuses` and `write:media`. Copy the access token it generates. Treat it like a password — anyone holding it can post as you.

Here's the entire posting logic, no framework, no wrapper, as a plain function you can drop into any script:

```python
import requests

def post_toot(instance_url, token, text, image_path=None):
    headers = {"Authorization": f"Bearer {token}"}
    media_ids = []

    if image_path:
        with open(image_path, "rb") as f:
            media_res = requests.post(
                f"{instance_url}/api/v1/media",
                headers=headers,
                files={"file": f},
            )
        media_res.raise_for_status()
        media_ids.append(media_res.json()["id"])

    status_data = {"status": text}
    if media_ids:
        status_data["media_ids[]"] = media_ids

    status_res = requests.post(
        f"{instance_url}/api/v1/statuses",
        headers=headers,
        data=status_data,
    )
    status_res.raise_for_status()
    return status_res.json()
```

Run this and check the return value — it's the full status object Mastodon stores, including the public `url` of your live toot. That single function is the whole bot. Everything after this is interface.

## Wrapping It in a UI Without Writing a Single Line of HTML

A function in a script is fine for you. It's useless for anyone who doesn't want to edit Python to change a caption. That gap — between "works in my terminal" and "someone else can use it" — is exactly where Streamlit earns its place.

`pip install streamlit requests` and you have a way to turn that function into a web form with password-masked inputs and a file uploader, without touching HTML, CSS, or a single frontend build step. If you've never used it: Streamlit reruns your whole script top to bottom on every interaction, and each `st.` call paints one widget. That mental model is all you need.

Here's the full app. Save it as `mastodon_bot.py`:

```python
import streamlit as st
import requests

st.set_page_config(page_title="Mastodon Bot", layout="centered")
st.title("Post to Mastodon with Python")

token = st.text_input("Access Token", type="password")
instance_url = st.text_input("Instance URL", value="https://me.dm")

if not token or not instance_url:
    st.warning("Enter your token and instance URL to continue.")
    st.stop()

headers = {"Authorization": f"Bearer {token}"}
text = st.text_area("Your toot", height=100)
image = st.file_uploader("Optional image", type=["png", "jpg", "jpeg", "gif"])

if st.button("Post Toot"):
    media_ids = []
    if image:
        media_res = requests.post(
            f"{instance_url}/api/v1/media",
            headers=headers,
            files={"file": (image.name, image, "application/octet-stream")},
        )
        if media_res.status_code != 200:
            st.error("Media upload failed.")
            st.json(media_res.json())
            st.stop()
        media_ids.append(media_res.json()["id"])

    payload = {"status": text}
    if media_ids:
        payload["media_ids[]"] = media_ids

    res = requests.post(
        f"{instance_url}/api/v1/statuses", headers=headers, data=payload
    )
    if res.status_code == 200:
        st.success("Posted.")
        st.markdown(f"[View your toot]({res.json()['url']})")
    else:
        st.error("Post failed.")
        st.json(res.json())
```

Then run `streamlit run mastodon_bot.py`. A local page opens at `localhost:8501` with a masked token field, a text box, and an image uploader. What to watch for on success: the app prints a clickable link straight to your live toot, pulled from the `url` field in the response — proof the round trip worked, not a green checkmark I hardcoded to show.

![person using a web application interface on a laptop](/content/blogs/2026-W29/2026-07-16_data_science_tech_building-a-mastodon-automation-bot-using-python-and-streamli_images/02_section2_person-using-a-web-application-interface-on-a-lapt.jpg)
*person using a web application interface on a laptop — Photo by [Jakub Zerdzicki](https://www.pexels.com/photo/close-up-of-programmer-typing-code-on-laptop-36496927/) on Pexels*

## The `raise_for_status()` Line That Saves You an Hour of Silent Failures

Here's what separates a script that works on your machine from one you'll still trust in three months: it fails loudly.

Notice `media_res.raise_for_status()` in the standalone function, and the explicit `status_code != 200` checks in the Streamlit version. These aren't decoration. The most common way a bot like this breaks is a token with the wrong scopes — you generated it with only `write:statuses` and forgot `write:media`, so the image upload returns a `403`, and the toot posts *without the picture*. No error, no crash — only a text post where you expected an image.

Without a status check, that `403` sails past silently. The `.json()` call on the error response is where the server tells you what went wrong — Mastodon returns a clean `{"error": "This action is outside the authorized scopes"}` message. Reading that one field is faster than any amount of guessing.

The same discipline applies to the token itself. Don't paste it into the script. The Streamlit version keeps it in a password field so it never touches your source, and for a headless cron-style bot, read it from an environment variable:

```python
import os
token = os.environ["MASTODON_TOKEN"]  # raises KeyError at startup if missing
```

That `os.environ[...]` — square brackets, not `.get()` — fails immediately at startup if the variable is missing, instead of failing later with a confusing `None` in your auth header. Fail at the boundary, where the message is obvious, not three calls deep where it isn't.

## When You *Should* Reach for the Library

I'm not anti-library. I'm anti-reaching-for-one-before-you've-looked-at-the-problem.

`Mastodon.py` is the right call the moment your needs cross a line: reading and paginating timelines, streaming live notifications over websockets, following and muting users, handling the full OAuth authorization flow for a multi-user app, or dealing with the dozens of edge cases in Mastodon's polls, scheduled statuses, and content warnings. That's real surface area, and hand-rolling it with `requests` would mean re-implementing exactly the thing the library already does well. At that point the dependency pays for itself.

The test I use, for any library, on any project: *am I calling three functions from this package, or thirty?* A posting bot calls two endpoints. If I pulled in `Mastodon.py` for that, I'd be importing a websocket client, a full pagination system, and an OAuth flow — to use none of it. When the ratio of what-I-use to what-I-import is that lopsided, the raw HTTP call is the honest choice.

This isn't about Mastodon. It's a habit worth building for every "there's a library for that" moment. Open the API docs first. Count the endpoints. If it's two, you already know how to call them.

## The Takeaway

The reflex to install a package the instant you hit a new API is expensive in a way that doesn't show up until later — in the dependency that breaks your build, the security advisory you now have to track, the abstraction you have to learn on top of the thing you were trying to do. Most of the time, the underlying API is simpler than the library wrapping it. You have to look before you install.

Automating Mastodon taught me nothing new about Mastodon. It reminded me of something about tools: the smallest thing that works is almost always the thing you'll still understand when it breaks. Forty lines you wrote beat four thousand you imported, every time you have to debug them at 2 a.m.

Next time you reach for `pip install`, open the API docs in the other tab first. Count the endpoints. You're probably already done.

## Before You Install the Next Wrapper

If this saved you a dependency, the best thing you can do is pass the habit on: next time a teammate reaches for a library to call two endpoints, send them the API docs instead. And if you want more of these — the small, practical calls a 10-year data scientist makes about what to build and what to skip — follow me here on Medium. I write about the unglamorous decisions that quietly decide whether your code is still maintainable a year from now.

<!-- Target keyphrase: automate mastodon python -->
<!-- SEO title: Automate Mastodon With Python — No Library Needed -->
<!-- SEO description: Automate Mastodon posts in Python with just requests and Streamlit — the simple way to post toots and images without the Mastodon.py library. -->

<!-- worksheet-cta -->

---

### Want to put this into practice?

[Download the companion worksheet →](https://worksheets-thebreathnetwork.vercel.app/get-worksheet/building-a-mastodon-automation-bot-using-python-and-streamli)

_Free PDF. Enter your email and it opens right away._
