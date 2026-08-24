const state = {
  cart: JSON.parse(localStorage.getItem("decor-cart") || "[]")
};
const drawer = document.querySelector("#cartDrawer");
const overlay = document.querySelector("#overlay");
const cartItems = document.querySelector("#cartItems");
const count = document.querySelector("#cartCount");
const total = document.querySelector("#cartTotal");
const result = document.querySelector("#checkoutResult");

function money(v){ return Number(String(v).replace(",", ".")).toLocaleString("pt-BR",{style:"currency",currency:"BRL"}); }
function save(){ localStorage.setItem("decor-cart", JSON.stringify(state.cart)); renderCart(); syncButtons(); }
function openCart(){ drawer.classList.add("open"); overlay.classList.add("open"); drawer.setAttribute("aria-hidden","false"); }
function closeCart(){ drawer.classList.remove("open"); overlay.classList.remove("open"); drawer.setAttribute("aria-hidden","true"); }

document.querySelector("#openCart").addEventListener("click", openCart);
document.querySelector("#heroCart").addEventListener("click", openCart);
document.querySelector("#closeCart").addEventListener("click", closeCart);
overlay.addEventListener("click", closeCart);

function addItem(btn){
  const item = {id:Number(btn.dataset.id), title:btn.dataset.title, price:btn.dataset.price, image:btn.dataset.image};
  if(!state.cart.some(x=>x.id===item.id)) state.cart.push(item);
  save();
  openCart();
}
document.querySelectorAll(".add-btn").forEach(btn=>btn.addEventListener("click",()=>addItem(btn)));

function removeItem(id){ state.cart = state.cart.filter(x=>x.id!==id); save(); }

function renderCart(){
  count.textContent = state.cart.length;
  if(!state.cart.length){
    cartItems.innerHTML = '<div class="empty">Você ainda não adicionou nenhuma decoração.</div>';
    total.textContent = money(0);
    return;
  }
  cartItems.innerHTML = state.cart.map(x=>`
    <div class="cart-item">
      <img src="${x.image}" alt="">
      <div><b>${x.title}</b><small>${money(x.price)}</small></div>
      <button aria-label="Remover" data-remove="${x.id}">×</button>
    </div>`).join("");
  cartItems.querySelectorAll("[data-remove]").forEach(b=>b.addEventListener("click",()=>removeItem(Number(b.dataset.remove))));
  const sum = state.cart.reduce((a,b)=>a+Number(String(b.price).replace(",",".")),0);
  total.textContent = money(sum);
}
function syncButtons(){
  document.querySelectorAll(".add-btn").forEach(btn=>{
    const exists = state.cart.some(x=>x.id===Number(btn.dataset.id));
    btn.classList.toggle("added", exists);
    btn.textContent = exists ? "Adicionado ✓" : "Adicionar ao pedido";
  });
}
renderCart(); syncButtons();

document.querySelectorAll(".filter").forEach(btn=>{
  btn.addEventListener("click",()=>{
    document.querySelectorAll(".filter").forEach(x=>x.classList.remove("active"));
    btn.classList.add("active");
    const f=btn.dataset.filter;
    document.querySelectorAll(".card").forEach(card=>card.classList.toggle("hidden",f!=="TODOS"&&card.dataset.category!==f));
  });
});

const modal=document.querySelector("#imageModal"), modalImage=document.querySelector("#modalImage");
document.querySelectorAll(".image-button").forEach(b=>b.addEventListener("click",()=>{
  modalImage.src=b.dataset.full; modal.showModal();
}));
document.querySelector("#closeModal").addEventListener("click",()=>modal.close());

document.querySelector("#checkoutForm").addEventListener("submit",async(e)=>{
  e.preventDefault();
  result.innerHTML="";
  if(!state.cart.length){ result.innerHTML='<div class="result-error">Escolha pelo menos uma decoração.</div>'; return; }

  const form = new FormData(e.currentTarget);
  const payload = {
    name: form.get("name"),
    whatsapp: form.get("whatsapp"),
    event_date: form.get("event_date"),
    notes: form.get("notes"),
    consent_whatsapp: form.get("consent_whatsapp") === "on",
    items: state.cart.map(x=>x.id)
  };
  const csrf = e.currentTarget.querySelector("[name=csrfmiddlewaretoken]").value;
  const submit=e.currentTarget.querySelector(".submit-order");
  submit.disabled=true; submit.textContent="Enviando...";
  try{
    const r=await fetch("/api/orders/",{
      method:"POST",
      headers:{"Content-Type":"application/json","X-CSRFToken":csrf},
      body:JSON.stringify(payload)
    });
    const data=await r.json();
    if(!r.ok) throw new Error(data.error||"Não foi possível enviar.");
    const wa = data.owner_whatsapp_link ? `<a href="${data.owner_whatsapp_link}" target="_blank" rel="noopener">Abrir conversa no WhatsApp →</a>` : "";
    result.innerHTML=`<div class="result-success"><b>Solicitação ${data.order_code} registrada!</b><br>Seu pedido já ficou salvo no sistema. Aguarde o contato para confirmação de disponibilidade e valor final.${wa}</div>`;
    state.cart=[]; save(); e.currentTarget.reset();
  }catch(err){
    result.innerHTML=`<div class="result-error">${err.message}</div>`;
  }finally{
    submit.disabled=false; submit.textContent="Enviar solicitação";
  }
});
