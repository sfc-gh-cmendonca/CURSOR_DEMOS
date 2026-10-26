// GTIF "Ask the Fund" backend: serves the React build and proxies chat
// requests to the Snowflake Cortex Agent REST API using key-pair (JWT) auth.
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import express from "express";
import rateLimit from "express-rate-limit";
import jwt from "jsonwebtoken";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const cfg = {
  port: Number(process.env.PORT || 8080),
  account: process.env.SNOWFLAKE_ACCOUNT || "SFSEEUROPE-EU_DEMO59",
  user: process.env.SNOWFLAKE_USER || "GTIF_DEMO_SVC",
  role: process.env.SNOWFLAKE_ROLE || "GTIF_DEMO_APP_RL",
  warehouse: process.env.SNOWFLAKE_WAREHOUSE || "ANALYTICS_WH",
  keyPath: process.env.SNOWFLAKE_PRIVATE_KEY_PATH || path.join(__dirname, "keys", "rsa_key.p8"),
  agentDb: "SNOWFLAKE_INTELLIGENCE",
  agentSchema: "AGENTS",
  agentName: process.env.AGENT_NAME || "GTIF_FUND_ANALYST",
  staticDir: process.env.STATIC_DIR || path.join(__dirname, "..", "web", "dist"),
  maxMessageChars: 2000,
  maxHistoryMessages: 24,
};

// Account host: lowercase, underscores become hyphens.
const host = `${cfg.account.toLowerCase().replace(/_/g, "-")}.snowflakecomputing.com`;
const privateKey = crypto.createPrivateKey(fs.readFileSync(cfg.keyPath));
const publicKeyDer = crypto.createPublicKey(privateKey).export({ type: "spki", format: "der" });
const fingerprint = "SHA256:" + crypto.createHash("sha256").update(publicKeyDer).digest("base64");
const qualifiedUser = `${cfg.account.toUpperCase()}.${cfg.user.toUpperCase()}`;

let cachedToken = { value: null, exp: 0 };
function snowflakeJwt() {
  const now = Math.floor(Date.now() / 1000);
  if (cachedToken.value && cachedToken.exp - now > 300) return cachedToken.value;
  const exp = now + 3600;
  const value = jwt.sign(
    { iss: `${qualifiedUser}.${fingerprint}`, sub: qualifiedUser, iat: now, exp },
    privateKey,
    { algorithm: "RS256" },
  );
  cachedToken = { value, exp };
  return value;
}

const app = express();
app.set("trust proxy", 1);
app.use(express.json({ limit: "512kb" }));

app.get("/api/health", (_req, res) => res.json({ ok: true, agent: cfg.agentName }));

const chatLimiter = rateLimit({
  windowMs: 10 * 60 * 1000,
  limit: 20,
  standardHeaders: "draft-7",
  legacyHeaders: false,
  message: { error: "Rate limit reached. Please wait a few minutes and try again." },
});

function validMessages(messages) {
  if (!Array.isArray(messages) || messages.length === 0 || messages.length > cfg.maxHistoryMessages) return false;
  const last = messages[messages.length - 1];
  if (last?.role !== "user") return false;
  const text = (last.content || []).filter((c) => c.type === "text").map((c) => c.text).join("");
  return text.length > 0 && text.length <= cfg.maxMessageChars;
}

app.post("/api/chat", chatLimiter, async (req, res) => {
  const { messages } = req.body || {};
  if (!validMessages(messages)) {
    return res.status(400).json({ error: `Invalid request (max ${cfg.maxMessageChars} characters per message).` });
  }

  const url = `https://${host}/api/v2/databases/${cfg.agentDb}/schemas/${cfg.agentSchema}/agents/${cfg.agentName}:run`;
  const controller = new AbortController();
  res.on("close", () => controller.abort());

  let upstream;
  try {
    upstream = await fetch(url, {
      method: "POST",
      signal: controller.signal,
      headers: {
        Authorization: `Bearer ${snowflakeJwt()}`,
        "X-Snowflake-Authorization-Token-Type": "KEYPAIR_JWT",
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ messages, stream: true }),
    });
  } catch (err) {
    console.error("Agent request failed:", err);
    return res.status(502).json({ error: "Could not reach Snowflake." });
  }

  if (!upstream.ok || !upstream.body) {
    const detail = await upstream.text().catch(() => "");
    console.error("Agent error", upstream.status, detail.slice(0, 500));
    return res.status(upstream.status || 502).json({ error: `Snowflake returned ${upstream.status}.` });
  }

  res.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache, no-transform",
    Connection: "keep-alive",
    "X-Accel-Buffering": "no",
  });
  try {
    for await (const chunk of upstream.body) res.write(chunk);
  } catch (err) {
    if (err.name !== "AbortError") console.error("Stream error:", err);
  }
  res.end();
});

app.use(express.static(cfg.staticDir));
app.get("*", (_req, res) => res.sendFile(path.join(cfg.staticDir, "index.html")));

app.listen(cfg.port, () => {
  console.log(`GTIF app on :${cfg.port} -> ${host} as ${cfg.user} (${cfg.role}), agent ${cfg.agentName}`);
});
