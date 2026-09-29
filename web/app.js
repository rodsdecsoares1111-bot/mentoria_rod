const state = {
  posts: [],
  platforms: {},
  filter: "all",
  search: "",
  sort: "score",
};

const numberFormat = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
const dateFormat = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", year: "numeric" });

function formatNumber(value) {
  return numberFormat.format(Number(value) || 0);
}

function availableMetric(post, key) {
  if (post.metric_availability && post.metric_availability[key] === false) return "—";
  if (post.platform === "linkedin" && !post.metrics_available) return "—";
  if (["views", "reach", "shares", "saves"].includes(key) && !post.metrics_available) return "—";
  return formatNumber(post[key]);
}

function setMetric(id, value) {
  document.getElementById(id).textContent = formatNumber(value);
}

function setNetworkStatus(platform, detail) {
  const element = document.getElementById(`${platform}-status`);
  const count = document.getElementById(`${platform}-count`);
  const states = {
    ok: `${detail.message || "Dados atualizados"}`,
    error: detail.message || "Falha na conexão",
    not_configured: "Credenciais não configuradas",
  };
  element.textContent = states[detail.state] || "Aguardando atualização";
  element.dataset.state = detail.state || "";
  count.textContent = detail.count == null ? "—" : `${formatNumber(detail.count)} posts`;
}

function renderSummary(posts) {
  setMetric("total-posts", posts.length);
  setMetric("total-views", posts.reduce((sum, post) => sum + (Number(post.views) || 0), 0));
  setMetric("total-interactions", posts.reduce((sum, post) => sum + ["likes", "shares", "saves", "clicks"].reduce((total, key) => total + (Number(post[key]) || 0), 0), 0));
  const best = posts.reduce((value, post) => Math.max(value, Number(post.score) || 0), 0);
  document.getElementById("best-score").textContent = posts.length ? best.toFixed(1) : "—";
  document.getElementById("all-filter-count").textContent = posts.length;
  document.getElementById("instagram-filter-count").textContent = posts.filter((post) => post.platform === "instagram").length;
  document.getElementById("linkedin-filter-count").textContent = posts.filter((post) => post.platform === "linkedin").length;
}

function createMetric(value, detail = "") {
  const metric = document.createElement("span");
  metric.className = "post-metric";
  if (value === "—") metric.classList.add("metric-unavailable");
  metric.textContent = value;
  if (detail) {
    const small = document.createElement("small");
    small.textContent = detail;
    metric.append(small);
  }
  return metric;
}

function createPostRow(post, index) {
  const row = document.createElement("article");
  row.className = "post-row";
  row.style.animationDelay = `${Math.min(index * 25, 200)}ms`;

  const content = document.createElement("div");
  content.className = "post-content";
  if (post.thumbnail) {
    const thumbnail = document.createElement("img");
    thumbnail.className = "post-thumb";
    thumbnail.src = post.thumbnail;
    thumbnail.alt = "";
    thumbnail.loading = "lazy";
    thumbnail.onerror = () => thumbnail.remove();
    content.append(thumbnail);
  } else {
    const placeholder = document.createElement("span");
    placeholder.className = "post-thumb is-empty";
    placeholder.textContent = post.platform === "linkedin" ? "in" : "ig";
    content.append(placeholder);
  }

  const copy = document.createElement("div");
  copy.className = "post-copy";
  const title = document.createElement(post.url ? "a" : "span");
  title.className = "post-title";
  title.textContent = post.title || "Publicação sem legenda";
  if (post.url) {
    title.href = post.url;
    title.target = "_blank";
    title.rel = "noreferrer";
  }
  const meta = document.createElement("span");
  meta.className = "post-meta";
  const platform = document.createElement("span");
  platform.className = `platform-pill ${post.platform}`;
  platform.textContent = post.platform === "instagram" ? "INSTAGRAM" : "LINKEDIN";
  const date = post.published_at ? dateFormat.format(new Date(post.published_at)) : "Data não informada";
  meta.append(platform, document.createTextNode(`· ${post.media_type || "Publicação"} · ${date}`));
  copy.append(title, meta);
  content.append(copy);
  row.append(content);

  const score = document.createElement("span");
  score.className = "post-score";
  const scoreText = document.createElement("span");
  scoreText.textContent = Number(post.score || 0).toFixed(1);
  const track = document.createElement("span");
  track.className = "score-track";
  const fill = document.createElement("span");
  fill.className = "score-fill";
  fill.style.width = `${Math.max(0, Math.min(Number(post.score) || 0, 100))}%`;
  track.append(fill);
  score.append(scoreText, track);
  row.append(score);

  row.append(
    createMetric(availableMetric(post, "views"), post.reach ? `${formatNumber(post.reach)} alcance` : ""),
    createMetric(availableMetric(post, "likes")),
    createMetric(availableMetric(post, "comments")),
    createMetric(availableMetric(post, "shares")),
    createMetric(availableMetric(post, "saves")),
    createMetric(availableMetric(post, "clicks")),
  );
  return row;
}

function renderPosts() {
  const list = document.getElementById("post-list");
  list.replaceChildren();
  const query = state.search.trim().toLocaleLowerCase("pt-BR");
  const posts = state.posts
    .filter((post) => state.filter === "all" || post.platform === state.filter)
    .filter((post) => !query || `${post.title} ${post.platform}`.toLocaleLowerCase("pt-BR").includes(query))
    .sort((first, second) => {
      if (state.sort === "date") return new Date(second.published_at || 0) - new Date(first.published_at || 0);
      if (state.sort === "views") return (Number(second.views) || 0) - (Number(first.views) || 0);
      return (Number(second.score) || 0) - (Number(first.score) || 0);
    });

  if (!posts.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    const hasPosts = state.posts.length > 0;
    empty.innerHTML = `<span class="empty-symbol">${hasPosts ? "⌕" : "↗"}</span><h3>${hasPosts ? "Nenhuma publicação encontrada" : "Seu conteúdo aparece aqui"}</h3><p>${hasPosts ? "Ajuste o filtro ou o termo de busca." : "Conecte as credenciais das redes e atualize os dados."}</p>`;
    list.append(empty);
    return;
  }
  posts.forEach((post, index) => list.append(createPostRow(post, index)));
}

function render(data) {
  state.posts = data.posts || [];
  state.platforms = data.platforms || {};
  renderSummary(state.posts);
  for (const platform of ["instagram", "linkedin"]) {
    setNetworkStatus(platform, state.platforms[platform] || {});
  }
  document.getElementById("updated-at").textContent = data.updated_at
    ? `Atualizado ${new Intl.DateTimeFormat("pt-BR", { dateStyle: "short", timeStyle: "short" }).format(new Date(data.updated_at))}`
    : "Aguardando primeira atualização";
  renderPosts();
}

async function loadPosts() {
  const response = await fetch("/api/posts", { cache: "no-store" });
  if (!response.ok) throw new Error("Não foi possível carregar o painel.");
  render(await response.json());
}

async function refreshPosts() {
  const button = document.getElementById("refresh-button");
  button.disabled = true;
  button.innerHTML = "<span aria-hidden=\"true\">↻</span> Buscando métricas...";
  try {
    const response = await fetch("/api/refresh", { method: "POST" });
    if (!response.ok) throw new Error("A atualização falhou.");
    render(await response.json());
  } catch (error) {
    document.getElementById("updated-at").textContent = error.message;
  } finally {
    button.disabled = false;
    button.innerHTML = "<span aria-hidden=\"true\">↻</span> Atualizar dados";
  }
}

document.getElementById("refresh-button").addEventListener("click", refreshPosts);
document.getElementById("search-input").addEventListener("input", (event) => {
  state.search = event.target.value;
  renderPosts();
});
document.getElementById("sort-select").addEventListener("change", (event) => {
  state.sort = event.target.value;
  renderPosts();
});
document.querySelectorAll(".filter-button").forEach((button) => {
  button.addEventListener("click", () => {
    state.filter = button.dataset.platform;
    document.querySelectorAll(".filter-button").forEach((item) => {
      const active = item === button;
      item.classList.toggle("is-active", active);
      item.setAttribute("aria-selected", String(active));
    });
    renderPosts();
  });
});

loadPosts().catch((error) => {
  document.getElementById("updated-at").textContent = error.message;
});