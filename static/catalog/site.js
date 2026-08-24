const state = {
  cart: JSON.parse(localStorage.getItem("decor-cart") || "[]"),
  filter: "TODOS",
  query: ""
};

const drawer = document.querySelector("#cartDrawer");
const overlay = document.querySelector("#overlay");
const cartItems = document.querySelector("#cartItems");
const count = document.querySelector("#cartCount");
const total = document.querySelector("#cartTotal");
const result = document.querySelector("#checkoutResult");
const search = document.querySelector("#catalogSearch");
const noResults = document.querySelector("#noResults");

function money(value){
  return Number(String(value).replace(",", ".")).toLocaleString("pt-BR", {style:"currency", currency:"BRL"});
}

function save(){
  localStorage.setItem("decor-cart", JSON.stringify(state.cart));
  renderCart();
  syncButtons();
}

function openCart(){
  drawer.classList.add("open");
  overlay.classList.add("open");
  drawer.setAttribute("aria-hidden", "false");
  document.body.classList.add("locked");
}

function closeCart(){
  drawer.classList.remove("open");
  overlay.classList.remove("open");
  drawer.setAttribute("aria-hidden", "true");
  document.body.classList.remove("locked");
}

document.querySelectorAll("#openCart,#heroCart,#ctaCart").forEach(btn => btn?.addEventListener("click", openCart));
document.querySelector("#closeCart")?.addEventListener("click", closeCart);
overlay?.addEventListener("click", closeCart);
document.addEventListener("keydown", e => { if(e.key === "Escape") closeCart(); });

function addItem(btn){
  const item = {
    id: Number(btn.dataset.id),
    title: btn.dataset.title,
    price: btn.dataset.price,
    image: btn.dataset.image
  };
  const exists = state.cart.some(x => x.id === item.id);
  if(!exists) state.cart.push(item);
  save();
  openCart();
}

document.querySelectorAll(".add-btn").forEach(btn => btn.addEventListener("click", () => addItem(btn)));

function removeItem(id){
  state.cart = state.cart.filter(x => x.id !== id);
  save();
}

function renderCart(){
  if(!count || !cartItems || !total) return;
  count.textContent = state.cart.length;

  if(!state.cart.length){
    cartItems.innerHTML = '<div class="empty">Sua seleção ainda está vazia.<br>Escolha uma decoração no portfólio para começar.</div>';
    total.textContent = money(0);
    return;
  }

  cartItems.innerHTML = state.cart.map(x => `
    <div class="cart-item">
      <img src="${x.image}" alt="">
      <div><b>${x.title}</b><small>${money(x.price)}</small></div>
      <button aria-label="Remover ${x.title}" data-remove="${x.id}" type="button">×</button>
    </div>`).join("");

  cartItems.querySelectorAll("[data-remove]").forEach(btn => {
    btn.addEventListener("click", () => removeItem(Number(btn.dataset.remove)));
  });

  const sum = state.cart.reduce((acc, item) => acc + Number(String(item.price).replace(",", ".")), 0);
  total.textContent = money(sum);
}

function syncButtons(){
  document.querySelectorAll(".add-btn").forEach(btn => {
    const exists = state.cart.some(x => x.id === Number(btn.dataset.id));
    btn.classList.toggle("added", exists);
    btn.querySelector("span").textContent = exists ? "Adicionado à solicitação" : "Adicionar à solicitação";
    btn.querySelector("b").textContent = exists ? "✓" : "＋";
  });
}

function applyCatalogFilters(){
  let visible = 0;
  document.querySelectorAll(".card").forEach(card => {
    const categoryOk = state.filter === "TODOS" || card.dataset.category === state.filter;
    const haystack = (card.dataset.search || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    const needle = state.query.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    const searchOk = !needle || haystack.includes(needle);
    const show = categoryOk && searchOk;
    card.classList.toggle("hidden", !show);
    if(show) visible += 1;
  });
  if(noResults) noResults.hidden = visible > 0;
}

document.querySelectorAll(".filter").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter").forEach(x => x.classList.remove("active"));
    btn.classList.add("active");
    state.filter = btn.dataset.filter;
    applyCatalogFilters();
  });
});

search?.addEventListener("input", () => {
  state.query = search.value.trim().toLowerCase();
  applyCatalogFilters();
});

const modal = document.querySelector("#imageModal");
const modalImage = document.querySelector("#modalImage");
document.querySelectorAll(".image-button").forEach(btn => {
  btn.addEventListener("click", () => {
    modalImage.src = btn.dataset.full;
    modalImage.alt = btn.querySelector("img")?.alt || "Decoração ampliada";
    modal.showModal();
  });
});
document.querySelector("#closeModal")?.addEventListener("click", () => modal.close());
modal?.addEventListener("click", e => {
  const rect = modal.getBoundingClientRect();
  if(e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) modal.close();
});

const form = document.querySelector("#checkoutForm");
form?.addEventListener("submit", async e => {
  e.preventDefault();
  result.innerHTML = "";

  if(!state.cart.length){
    result.innerHTML = '<div class="result-error">Escolha pelo menos uma decoração antes de enviar.</div>';
    return;
  }

  const data = new FormData(form);
  const payload = {
    name: data.get("name"),
    whatsapp: data.get("whatsapp"),
    event_date: data.get("event_date"),
    notes: data.get("notes"),
    consent_whatsapp: data.get("consent_whatsapp") === "on",
    items: state.cart.map(x => x.id)
  };

  const csrf = form.querySelector("[name=csrfmiddlewaretoken]").value;
  const submit = form.querySelector(".submit-order");
  const original = submit.innerHTML;
  submit.disabled = true;
  submit.innerHTML = "<span>Registrando sua solicitação...</span><b>•••</b>";

  try{
    const response = await fetch("/api/orders/", {
      method: "POST",
      headers: {"Content-Type":"application/json", "X-CSRFToken":csrf},
      body: JSON.stringify(payload)
    });
    const json = await response.json();
    if(!response.ok) throw new Error(json.error || "Não foi possível enviar sua solicitação.");

    const whatsapp = json.owner_whatsapp_link
      ? `<a href="${json.owner_whatsapp_link}" target="_blank" rel="noopener">Continuar no WhatsApp →</a>`
      : "";

    result.innerHTML = `<div class="result-success"><b>Solicitação ${json.order_code} registrada com sucesso.</b><br>As decoradoras já têm os dados do seu pedido. Use o botão abaixo para continuar o atendimento.${whatsapp}</div>`;
    state.cart = [];
    save();
    form.reset();
  }catch(error){
    result.innerHTML = `<div class="result-error">${error.message}</div>`;
  }finally{
    submit.disabled = false;
    submit.innerHTML = original;
  }
});

renderCart();
syncButtons();
applyCatalogFilters();

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if(entry.isIntersecting){
      entry.target.classList.add("visible");
      observer.unobserve(entry.target);
    }
  });
}, {threshold:.08, rootMargin:"0px 0px -30px 0px"});

document.querySelectorAll(".reveal").forEach(el => observer.observe(el));
