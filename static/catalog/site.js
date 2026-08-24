const state = {
  cart: JSON.parse(localStorage.getItem("decor-inspirations") || "[]"),
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
  localStorage.setItem("decor-inspirations", JSON.stringify(state.cart));
  renderCart(); syncButtons();
}
function openCart(){
  drawer?.classList.add("open"); overlay?.classList.add("open");
  drawer?.setAttribute("aria-hidden", "false"); document.body.classList.add("locked");
}
function closeCart(){
  drawer?.classList.remove("open"); overlay?.classList.remove("open");
  drawer?.setAttribute("aria-hidden", "true"); document.body.classList.remove("locked");
}

document.querySelectorAll("#openCart,#heroCart,#ctaCart").forEach(btn => btn?.addEventListener("click", openCart));
document.querySelector("#closeCart")?.addEventListener("click", closeCart);
overlay?.addEventListener("click", closeCart);
document.addEventListener("keydown", e => { if(e.key === "Escape") closeCart(); });

function addItem(btn){
  const item = {id:Number(btn.dataset.id), title:btn.dataset.title, price:btn.dataset.price, image:btn.dataset.image};
  if(!state.cart.some(x => x.id === item.id)) state.cart.push(item);
  save(); openCart();
}
document.querySelectorAll(".add-btn").forEach(btn => btn.addEventListener("click", () => addItem(btn)));
function removeItem(id){ state.cart = state.cart.filter(x => x.id !== id); save(); }

function renderCart(){
  if(!count || !cartItems || !total) return;
  count.textContent = state.cart.length;
  if(!state.cart.length){
    cartItems.innerHTML = '<div class="empty"><b>Nenhuma inspiração escolhida.</b><br>Volte ao portfólio e escolha uma referência para personalizar.</div>';
    total.textContent = money(0); return;
  }
  cartItems.innerHTML = state.cart.map(x => `
    <div class="cart-item">
      <img src="${x.image}" alt="">
      <div><b>${x.title}</b><small>Referência ${money(x.price)}</small></div>
      <button aria-label="Remover ${x.title}" data-remove="${x.id}" type="button">×</button>
    </div>`).join("");
  cartItems.querySelectorAll("[data-remove]").forEach(btn => btn.addEventListener("click", () => removeItem(Number(btn.dataset.remove))));
  const sum = state.cart.reduce((acc, item) => acc + Number(String(item.price).replace(",", ".")), 0);
  total.textContent = money(sum);
}

function syncButtons(){
  document.querySelectorAll(".add-btn").forEach(btn => {
    const exists = state.cart.some(x => x.id === Number(btn.dataset.id));
    btn.classList.toggle("added", exists);
    const text = btn.querySelector("span");
    const icon = btn.querySelector("b");
    if(text) text.textContent = exists ? "Inspiração selecionada" : "Quero esta inspiração";
    if(icon) icon.textContent = exists ? "✓" : "＋";
  });
}

function normalizeText(value){ return (value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase(); }
function applyCatalogFilters(){
  let visible = 0;
  document.querySelectorAll(".card").forEach(card => {
    const categoryOk = state.filter === "TODOS" || card.dataset.category === state.filter;
    const searchOk = !state.query || normalizeText(card.dataset.search).includes(normalizeText(state.query));
    const show = categoryOk && searchOk;
    card.classList.toggle("hidden", !show);
    if(show) visible += 1;
  });
  if(noResults) noResults.hidden = visible > 0;
}
document.querySelectorAll(".filter").forEach(btn => btn.addEventListener("click", () => {
  document.querySelectorAll(".filter").forEach(x => x.classList.remove("active"));
  btn.classList.add("active"); state.filter = btn.dataset.filter; applyCatalogFilters();
}));
search?.addEventListener("input", () => { state.query = search.value.trim(); applyCatalogFilters(); });

const modal = document.querySelector("#imageModal");
const modalImage = document.querySelector("#modalImage");
document.querySelectorAll(".image-button").forEach(btn => btn.addEventListener("click", () => {
  modalImage.src = btn.dataset.full; modalImage.alt = btn.querySelector("img")?.alt || "Inspiração ampliada"; modal.showModal();
}));
document.querySelector("#closeModal")?.addEventListener("click", () => modal.close());

const form = document.querySelector("#checkoutForm");
form?.addEventListener("submit", async e => {
  e.preventDefault(); result.innerHTML = "";
  if(!state.cart.length){ result.innerHTML = '<div class="result-error">Escolha pelo menos uma inspiração antes de continuar.</div>'; return; }

  const data = new FormData(form);
  const payload = {
    name: data.get("name"),
    whatsapp: data.get("whatsapp"),
    event_type: data.get("event_type"),
    event_theme: data.get("event_theme"),
    celebrant_name: data.get("celebrant_name"),
    celebrant_age: data.get("celebrant_age"),
    event_date: data.get("event_date"),
    event_location: data.get("event_location"),
    keep_details: data.get("keep_details"),
    change_details: data.get("change_details"),
    notes: data.get("notes"),
    consent_whatsapp: data.get("consent_whatsapp") === "on",
    items: state.cart.map(x => x.id)
  };

  const csrf = form.querySelector("[name=csrfmiddlewaretoken]").value;
  const submit = form.querySelector(".submit-order");
  const original = submit.innerHTML;
  submit.disabled = true; submit.innerHTML = "<span>Registrando e preparando WhatsApp...</span><b>•••</b>";

  try{
    const response = await fetch("/api/orders/", {
      method:"POST", headers:{"Content-Type":"application/json","X-CSRFToken":csrf}, body:JSON.stringify(payload)
    });
    const json = await response.json();
    if(!response.ok) throw new Error(json.error || "Não foi possível registrar sua solicitação.");

    state.cart = []; save();
    result.innerHTML = `<div class="result-success"><b>Solicitação ${json.order_code} registrada.</b><br>Agora vamos abrir o WhatsApp com todos os detalhes prontos. Basta conferir e tocar em <b>Enviar</b>.</div>`;

    if(json.owner_whatsapp_link){
      setTimeout(() => { window.location.href = json.owner_whatsapp_link; }, 450);
    } else {
      result.innerHTML += '<div class="result-error">O WhatsApp das decoradoras ainda não foi configurado no painel.</div>';
    }
  }catch(error){
    result.innerHTML = `<div class="result-error">${error.message}</div>`;
  }finally{
    submit.disabled = false; submit.innerHTML = original;
  }
});

renderCart(); syncButtons(); applyCatalogFilters();

if("IntersectionObserver" in window){
  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
    if(entry.isIntersecting){ entry.target.classList.add("visible"); observer.unobserve(entry.target); }
  }), {threshold:.08, rootMargin:"0px 0px -25px 0px"});
  document.querySelectorAll(".reveal").forEach(el => observer.observe(el));
}else{
  document.querySelectorAll(".reveal").forEach(el => el.classList.add("visible"));
}
