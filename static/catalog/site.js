const siteHeader = document.querySelector("#siteHeader");
function syncHeader(){
  if(!siteHeader) return;
  siteHeader.classList.toggle("scrolled", window.scrollY > 28);
}
syncHeader();
window.addEventListener("scroll", syncHeader, {passive:true});

const mobileMenuToggle = document.querySelector("#mobileMenuToggle");
const mobileNav = document.querySelector("#mobileNav");

function setMobileMenu(open){
  if(!mobileMenuToggle || !mobileNav) return;
  mobileNav.hidden = !open;
  mobileMenuToggle.setAttribute("aria-expanded", String(open));
  mobileMenuToggle.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
}

mobileMenuToggle?.addEventListener("click", () => {
  setMobileMenu(mobileNav?.hidden ?? true);
});

mobileNav?.querySelectorAll("a").forEach(link =>
  link.addEventListener("click", () => setMobileMenu(false))
);


function loadCart(){
  try{
    const parsed = JSON.parse(localStorage.getItem("decor-inspirations") || "[]");
    if(!Array.isArray(parsed)) return [];
    return parsed
      .filter(item => item && Number.isFinite(Number(item.id)))
      .slice(0, 10)
      .map(item => ({
        id:Number(item.id),
        title:String(item.title || "").slice(0, 180),
        price:String(item.price || "0"),
        image:String(item.image || "").slice(0, 1000)
      }));
  }catch(error){
    localStorage.removeItem("decor-inspirations");
    return [];
  }
}

function escapeHtml(value){
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&":"&amp;",
    "<":"&lt;",
    ">":"&gt;",
    '"':"&quot;",
    "'":"&#039;"
  })[char]);
}

const state = {
  cart: loadCart(),
  filter: "TODOS",
  query: "",
  drawerStep: "summary"
};

const drawer = document.querySelector("#cartDrawer");
const overlay = document.querySelector("#overlay");
const cartItems = document.querySelector("#cartItems");
const count = document.querySelector("#cartCount");
const total = document.querySelector("#cartTotal");
const result = document.querySelector("#checkoutResult");
const search = document.querySelector("#catalogSearch");
const noResults = document.querySelector("#noResults");

const summaryStep = document.querySelector("#drawerSummaryStep");
const formStep = document.querySelector("#drawerFormStep");
const summaryEmpty = document.querySelector("#summaryEmpty");
const summarySelected = document.querySelector("#summarySelected");
const continueBtn = document.querySelector("#continuePersonalization");
const backSummaryBtn = document.querySelector("#backToSummary");
const backCatalogBtn = document.querySelector("#backToCatalog");
const addMoreBtn = document.querySelector("#addMoreInspirations");

function money(value){
  return Number(String(value).replace(",", ".")).toLocaleString("pt-BR", {
    style:"currency", currency:"BRL"
  });
}

function save(){
  localStorage.setItem("decor-inspirations", JSON.stringify(state.cart));
  renderCart();
  syncButtons();
}

function showDrawerStep(step){
  state.drawerStep = step === "form" && state.cart.length ? "form" : "summary";
  const isSummary = state.drawerStep === "summary";
  if(summaryStep){
    summaryStep.hidden = !isSummary;
    summaryStep.classList.toggle("active", isSummary);
  }
  if(formStep){
    formStep.hidden = isSummary;
    formStep.classList.toggle("active", !isSummary);
  }
  if(drawer) drawer.scrollTop = 0;
}

function openCart(step="summary"){
  drawer?.classList.add("open");
  overlay?.classList.add("open");
  drawer?.setAttribute("aria-hidden", "false");
  document.body.classList.add("locked");
  showDrawerStep(step);
}

function closeCart(){
  drawer?.classList.remove("open");
  overlay?.classList.remove("open");
  drawer?.setAttribute("aria-hidden", "true");
  document.body.classList.remove("locked");
}

document.querySelectorAll("#openCart,#heroCart,#ctaCart").forEach(btn =>
  btn?.addEventListener("click", () => openCart("summary"))
);
document.querySelector("#closeCart")?.addEventListener("click", closeCart);
overlay?.addEventListener("click", closeCart);
document.addEventListener("keydown", e => { if(e.key === "Escape") closeCart(); });

continueBtn?.addEventListener("click", () => {
  if(!state.cart.length) return;
  showDrawerStep("form");
});

backSummaryBtn?.addEventListener("click", () => showDrawerStep("summary"));

function returnToCatalog(){
  closeCart();
  setTimeout(() => document.querySelector("#catalogo")?.scrollIntoView({behavior:"smooth", block:"start"}), 120);
}
backCatalogBtn?.addEventListener("click", returnToCatalog);
addMoreBtn?.addEventListener("click", returnToCatalog);

function addItem(btn){
  const item = {
    id:Number(btn.dataset.id),
    title:btn.dataset.title,
    price:btn.dataset.price,
    image:btn.dataset.image
  };
  if(!state.cart.some(x => x.id === item.id)) state.cart.push(item);
  save();
  openCart("summary");
}

document.querySelectorAll(".add-btn").forEach(btn =>
  btn.addEventListener("click", () => addItem(btn))
);

function removeItem(id){
  state.cart = state.cart.filter(x => x.id !== id);
  save();
  if(!state.cart.length) showDrawerStep("summary");
}

function renderCart(){
  if(count) count.textContent = state.cart.length;

  if(summaryEmpty) summaryEmpty.hidden = state.cart.length > 0;
  if(summarySelected) summarySelected.hidden = state.cart.length === 0;

  if(!cartItems || !total) return;

  if(!state.cart.length){
    cartItems.innerHTML = "";
    total.textContent = money(0);
    return;
  }

  cartItems.innerHTML = state.cart.map(x => `
    <div class="cart-item">
      <img src="${escapeHtml(x.image)}" alt="">
      <div>
        <b>${escapeHtml(x.title)}</b>
        <small>Referência ${money(x.price)}</small>
      </div>
      <button aria-label="Remover ${escapeHtml(x.title)}" data-remove="${x.id}" type="button">×</button>
    </div>
  `).join("");

  cartItems.querySelectorAll("[data-remove]").forEach(btn =>
    btn.addEventListener("click", () => removeItem(Number(btn.dataset.remove)))
  );

  const sum = state.cart.reduce(
    (acc, item) => acc + Number(String(item.price).replace(",", ".")), 0
  );
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

function normalizeText(value){
  return (value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

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
  btn.classList.add("active");
  state.filter = btn.dataset.filter;
  applyCatalogFilters();
}));

search?.addEventListener("input", () => {
  state.query = search.value.trim();
  applyCatalogFilters();
});


const whatsappChooser = document.querySelector("#whatsappChooser");

function setWhatsappChoiceRoutes(routes=null){
  document.querySelectorAll(".wa-choice[data-wa-person]").forEach(choice => {
    const person = choice.dataset.waPerson;

    // Pedido recém-criado: o servidor recompõe toda a mensagem e redireciona.
    if(routes?.[person]){
      choice.href = routes[person];
      return;
    }

    // Contato geral: também passa pelo Django; nenhum emoji trafega no JS.
    choice.href = `/api/whatsapp/${encodeURIComponent(person)}/`;
  });
}

function openWhatsappChooser(routes=null){
  const choices = document.querySelectorAll(".wa-choice[data-wa-person]");
  if(!choices.length) return;
  setWhatsappChoiceRoutes(routes);
  whatsappChooser?.showModal();
}

function closeWhatsappChooser(){
  whatsappChooser?.close();
}

document.querySelectorAll(".open-whatsapp-selector").forEach(btn =>
  btn.addEventListener("click", () => openWhatsappChooser())
);

document.querySelector("#closeWhatsappChooser")?.addEventListener(
  "click",
  closeWhatsappChooser
);

whatsappChooser?.addEventListener("click", event => {
  const rect = whatsappChooser.getBoundingClientRect();
  const inside = event.clientX >= rect.left && event.clientX <= rect.right &&
                 event.clientY >= rect.top && event.clientY <= rect.bottom;
  if(!inside) closeWhatsappChooser();
});


const gpsButton = document.querySelector("#useGpsLocation");
const gpsStatus = document.querySelector("#gpsStatus");

function field(name){
  return form?.querySelector(`[name="${name}"]`);
}

function setField(name, value, overwrite=false){
  const input = field(name);
  if(!input || value === undefined || value === null || value === "") return;
  if(overwrite || !input.value.trim()) input.value = String(value);
}

function gpsMessage(text, type=""){
  if(!gpsStatus) return;
  gpsStatus.textContent = text;
  gpsStatus.className = `gps-status ${type}`.trim();
}

async function reverseGeocode(lat, lon){
  const url = new URL("https://nominatim.openstreetmap.org/reverse");
  url.searchParams.set("format", "jsonv2");
  url.searchParams.set("lat", lat);
  url.searchParams.set("lon", lon);
  url.searchParams.set("addressdetails", "1");
  url.searchParams.set("accept-language", "pt-BR");

  const response = await fetch(url.toString(), {
    headers:{"Accept":"application/json"}
  });
  if(!response.ok) throw new Error("reverse-geocode-failed");
  return response.json();
}

function fillAddressFromGps(result){
  const a = result?.address || {};
  const city = a.city || a.town || a.municipality || a.village || "";
  const neighborhood =
    a.neighbourhood || a.suburb || a.quarter || a.city_district || "";
  const street = a.road || a.pedestrian || a.residential || "";
  const state = a.state_code || a.state || "";

  setField("event_city", city, true);
  setField("event_state", state, true);
  setField("event_neighborhood", neighborhood, true);
  setField("event_street", street, true);
  setField("event_number", a.house_number || "", true);
  setField("event_postcode", a.postcode || "", true);
}

gpsButton?.addEventListener("click", () => {
  if(!navigator.geolocation){
    gpsMessage("Este navegador não oferece localização por GPS. Preencha o endereço manualmente.", "error");
    return;
  }

  gpsButton.disabled = true;
  gpsButton.textContent = "Localizando...";
  gpsMessage("Aguardando autorização de localização do aparelho...", "loading");

  navigator.geolocation.getCurrentPosition(
    async position => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;

      setField("event_latitude", lat.toFixed(7), true);
      setField("event_longitude", lon.toFixed(7), true);

      try{
        gpsMessage("Localização encontrada. Buscando rua e bairro...", "loading");
        const result = await reverseGeocode(lat, lon);
        fillAddressFromGps(result);
        gpsMessage("Endereço preenchido pelo GPS. Confira os campos antes de enviar.", "success");
      }catch(error){
        gpsMessage("GPS capturado, mas não foi possível descobrir o endereço automaticamente. Você pode preencher manualmente.", "warning");
      }finally{
        gpsButton.disabled = false;
        gpsButton.textContent = "Atualizar GPS";
      }
    },
    error => {
      const messages = {
        1:"Permissão de localização negada. Você pode preencher o endereço manualmente.",
        2:"Não foi possível obter a localização do aparelho.",
        3:"A localização demorou demais. Tente novamente."
      };
      gpsMessage(messages[error.code] || "Não foi possível usar o GPS.", "error");
      gpsButton.disabled = false;
      gpsButton.textContent = "Tentar GPS novamente";
    },
    {
      enableHighAccuracy:true,
      timeout:12000,
      maximumAge:60000
    }
  );
});

document.querySelectorAll("[data-guests]").forEach(button => {
  button.addEventListener("click", () => {
    const input = document.querySelector("#guestCount");
    if(!input) return;
    input.value = button.dataset.guests;
    input.focus();
  });
});


const modal = document.querySelector("#imageModal");
const modalImage = document.querySelector("#modalImage");


document.querySelectorAll(".image-button").forEach(btn => btn.addEventListener("click", () => {
  if(!modal || !modalImage) return;
  modalImage.src = btn.dataset.full;
  modalImage.alt = btn.querySelector("img")?.alt || "Inspiração ampliada";
  modal.showModal();
}));
document.querySelector("#closeModal")?.addEventListener("click", () => modal?.close());

const form = document.querySelector("#checkoutForm");

form?.addEventListener("submit", async e => {
  e.preventDefault();
  if(result) result.innerHTML = "";

  if(!state.cart.length){
    if(result) result.innerHTML = '<div class="result-error">Escolha pelo menos uma inspiração antes de continuar.</div>';
    showDrawerStep("summary");
    return;
  }

  const data = new FormData(form);
  const payload = {
    name: data.get("name"),
    whatsapp: data.get("whatsapp"),
    event_type: data.get("event_type"),
    event_theme: data.get("event_theme"),
    celebrant_name: data.get("celebrant_name"),
    celebrant_age: data.get("celebrant_age"),
    event_date: data.get("event_date"),
    event_venue: data.get("event_venue"),
    event_city: data.get("event_city"),
    event_state: data.get("event_state"),
    event_neighborhood: data.get("event_neighborhood"),
    event_street: data.get("event_street"),
    event_number: data.get("event_number"),
    event_complement: data.get("event_complement"),
    event_reference: data.get("event_reference"),
    event_postcode: data.get("event_postcode"),
    event_latitude: data.get("event_latitude"),
    event_longitude: data.get("event_longitude"),
    guest_count: data.get("guest_count"),
    keep_choices: data.getAll("keep_choices"),
    change_choices: data.getAll("change_choices"),
    keep_details: data.get("keep_details"),
    change_details: data.get("change_details"),
    notes: data.get("notes"),
    consent_whatsapp: data.get("consent_whatsapp") === "on",
    website: data.get("website") || "",
    items: state.cart.map(x => x.id)
  };

  const csrf = form.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
  const submit = form.querySelector(".submit-order");
  const original = submit?.innerHTML || "";

  if(submit){
    submit.disabled = true;
    submit.innerHTML = "<span>Registrando e preparando WhatsApp...</span><b>•••</b>";
  }

  try{
    const response = await fetch("/api/orders/", {
      method:"POST",
      headers:{"Content-Type":"application/json","X-CSRFToken":csrf},
      body:JSON.stringify(payload)
    });
    const json = await response.json();
    if(!response.ok) throw new Error(json.error || "Não foi possível registrar sua solicitação.");

    state.cart = [];
    save();

    if(result){
      result.innerHTML = `
        <div class="result-success">
          <b>Solicitação ${json.order_code} registrada.</b><br>
          Agora vamos abrir o WhatsApp com todos os detalhes prontos.
          Basta conferir e tocar em <b>Enviar</b>.
        </div>`;
    }

    const routes = json.whatsapp_routes || null;
    if(document.querySelectorAll(".wa-choice[data-wa-person]").length){
      setTimeout(() => { closeCart(); openWhatsappChooser(routes); }, 450);
    }else if(result){
      result.innerHTML += '<div class="result-error">Cadastre pelo menos um WhatsApp das decoradoras no painel administrativo.</div>';
    }
  }catch(error){
    if(result) result.innerHTML = `<div class="result-error">${escapeHtml(error.message)}</div>`;
  }finally{
    if(submit){
      submit.disabled = false;
      submit.innerHTML = original;
    }
  }
});

const eventDateInput = form?.querySelector('[name="event_date"]');
if(eventDateInput){
  const today = new Date();
  const localDate = new Date(today.getTime() - today.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 10);
  eventDateInput.min = localDate;
}

renderCart();
syncButtons();
applyCatalogFilters();
showDrawerStep("summary");

if("IntersectionObserver" in window){
  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
    if(entry.isIntersecting){
      entry.target.classList.add("visible");
      observer.unobserve(entry.target);
    }
  }), {threshold:.08, rootMargin:"0px 0px -25px 0px"});
  document.querySelectorAll(".reveal").forEach(el => observer.observe(el));
}else{
  document.querySelectorAll(".reveal").forEach(el => el.classList.add("visible"));
}
