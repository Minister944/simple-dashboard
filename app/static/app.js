const grid = document.getElementById("grid");

function renderTile(stack) {
  const cfg = stack;
  const label = cfg.label || stack.name;

  const tile = document.createElement(cfg.url ? "a" : "div");
  tile.className = "tile";
  if (cfg.url) tile.href = cfg.url;

  const img = document.createElement("img");
  img.src = `/static/img/${cfg.img || stack.name}.webp`;
  img.alt = stack.name;
  img.onerror = () => {
    const fb = document.createElement("div");
    fb.className = "fallback";
    fb.textContent = stack.name[0].toUpperCase();
    img.replaceWith(fb);
  };

  tile.innerHTML = `
    <span class="dot ${stack.status === "running" ? "running" : "stopped"}"
          title="${stack.status}"></span>
    <div class="name">${label}</div>
    <div class="desc">${cfg.desc}</div>`;
  tile.prepend(img);

  if (cfg.startable && stack.status !== "running") {
    const btn = document.createElement("button");
    btn.className = "start";
    btn.textContent = "Start";
    btn.onclick = async (e) => {
      e.preventDefault();
      btn.disabled = true;
      btn.textContent = "Uruchamiam…";
      try {
        const res = await fetch(`/start/${stack.name}`);
        if (!res.ok) throw new Error(res.status);
        setTimeout(load, 3000);
      } catch {
        btn.disabled = false;
        btn.textContent = "Błąd - spróbuj ponownie";
      }
    };
    tile.append(btn);
  }

  return tile;
}

async function load() {
  const res = await fetch("/stacks");
  const stacks = await res.json();
  grid.replaceChildren(...stacks.map(renderTile));
}

load();
setInterval(load, 30000);
