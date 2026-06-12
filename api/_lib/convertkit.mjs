// Kit (ConvertKit) v4 client. Verified against developers.kit.com.
// Auth: custom header X-Kit-Api-Key (NOT Authorization: Bearer — that's OAuth).
const BASE_URL = "https://api.kit.com/v4";

const tagIdCache = new Map(); // name -> id, per cold start

function apiKey() {
  const k = process.env.CONVERTKIT_API_KEY;
  if (!k) throw new Error("CONVERTKIT_API_KEY is not set");
  return k;
}

async function kit(path, { method = "GET", body } = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: {
      "X-Kit-Api-Key": apiKey(),
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Kit API ${method} ${path} -> ${res.status}: ${text.slice(0, 300)}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

// Returns true if the email already exists in the Kit database.
export async function subscriberExists(email) {
  const data = await kit(`/subscribers?email_address=${encodeURIComponent(email)}`);
  return Array.isArray(data?.subscribers) && data.subscribers.length > 0;
}

// POST /subscribers is an upsert (body { email_address }). Returns
// { subscriber: { id, ... } }. Call subscriberExists() first to classify.
export async function upsertSubscriber(email) {
  const data = await kit(`/subscribers`, {
    method: "POST",
    body: { email_address: email },
  });
  return data?.subscriber ?? null;
}

export async function resolveTagId(name) {
  if (tagIdCache.has(name)) return tagIdCache.get(name);
  const data = await kit(`/tags`);
  for (const t of data?.tags ?? []) tagIdCache.set(t.name, t.id);
  if (!tagIdCache.has(name)) {
    const created = await kit(`/tags`, { method: "POST", body: { name } });
    tagIdCache.set(name, created?.tag?.id);
  }
  return tagIdCache.get(name);
}

// POST /v4/tags/{tag_id}/subscribers/{subscriber_id} — empty body. Tag by
// numeric subscriber id (the email-in-path form does not exist in v4).
export async function tagSubscriber(subscriberId, tagId) {
  return kit(`/tags/${tagId}/subscribers/${subscriberId}`, {
    method: "POST",
    body: {},
  });
}

// Full flow: classify, upsert, tag. Returns "first_time" | "returning".
export async function captureAndTag(email) {
  const exists = await subscriberExists(email);
  const subscriber = await upsertSubscriber(email); // safe whether new or returning
  if (!subscriber?.id) throw new Error("Kit upsert returned no subscriber id");

  const tagName = exists ? "worksheet_repeat_visitor" : "first_time_worksheet";
  const tagId = await resolveTagId(tagName);
  if (tagId) await tagSubscriber(subscriber.id, tagId);
  return exists ? "returning" : "first_time";
}
