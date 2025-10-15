let currentCardId = null;
let currentBalance = 0;
let menu = [];
let cart = [];

const cardIdEl = document.getElementById('cardId');
const cardBalEl = document.getElementById('cardBalance');
const addAmount = document.getElementById('addAmount');
const addBtn = document.getElementById('addBtn');
const addMsg = document.getElementById('addMsg');
const orderBtn = document.getElementById('orderBtn');
const orderMsg = document.getElementById('orderMsg');
const menuList = document.getElementById('menuList');

// ---- Poll card from Flask ----
async function pollCard() {
  try {
    const res = await fetch('/api/latest-card');
    const data = await res.json();
    if (data.rfid_card_id && data.rfid_card_id !== currentCardId) {
      currentCardId = data.rfid_card_id;
      cardIdEl.innerText = currentCardId;
      await fetchBalance();
    }
  } catch (err) {
    console.error("Polling error:", err);
  }
}

async function fetchBalance() {
  const res = await fetch('/api/students');
  const students = await res.json();
  const s = students.find(x => x.rfid_card_id === currentCardId);
  cardBalEl.innerText = s ? s.balance : 0;
}

setInterval(pollCard, 1000); // check every second

// ---- Fetch menu ----
async function fetchMenu() {
  const res = await fetch('/api/menu');
  menu = await res.json();
  renderMenu();
}

function renderMenu() {
  menuList.innerHTML = '';
  menu.forEach(item => {
    const div = document.createElement('div');
    div.className = 'columns is-vcentered';
    div.innerHTML = `
      <div class="column">${item.food} — ₹${item.price}</div>
      <div class="column is-narrow">
        <button class="button is-small is-link" data-food="${item.food}">+1</button>
        <button class="button is-small is-light" data-remove="${item.food}">-1</button>
        <span id="qty-${item.food.replace(/\s+/g, '_')}">0</span>
      </div>
    `;
    menuList.appendChild(div);
  });

  document.querySelectorAll('[data-food]').forEach(btn =>
    btn.addEventListener('click', () => addToCart(btn.dataset.food, 1))
  );
  document.querySelectorAll('[data-remove]').forEach(btn =>
    btn.addEventListener('click', () => addToCart(btn.dataset.remove, -1))
  );
}

function addToCart(food, delta) {
  const existing = cart.find(c => c.food === food);
  if (existing) {
    existing.qty = Math.max(0, existing.qty + delta);
    if (existing.qty === 0) cart = cart.filter(c => c.food !== food);
  } else if (delta > 0) {
    cart.push({ food, qty: 1 });
  }
  updateQtyDisplay();
}

function updateQtyDisplay() {
  menu.forEach(item => {
    const el = document.getElementById('qty-' + item.food.replace(/\s+/g, '_'));
    const found = cart.find(c => c.food === item.food);
    if (el) el.innerText = found ? found.qty : 0;
  });
}

// ---- Add balance ----
addBtn.addEventListener('click', async () => {
  if (!currentCardId) return alert('Scan a card first.');
  const amt = parseFloat(addAmount.value);
  if (!amt || amt <= 0) return alert('Enter valid amount.');

  const res = await fetch('/api/add-balance', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rfid_card_id: currentCardId, amount: amt })
  });
  const data = await res.json();
  if (res.ok) {
    addMsg.innerText = `Added ₹${amt}. New balance ₹${data.newBalance.toFixed(2)}`;
    currentBalance = data.newBalance;
    cardBalEl.innerText = currentBalance.toFixed(2);
    addAmount.value = '';
  } else {
    addMsg.innerText = 'Error: ' + (data.error || 'unknown');
  }
});

// ---- Place order ----
orderBtn.addEventListener('click', async () => {
  if (!currentCardId) return alert('Scan a card first.');
  if (!cart.length) return alert('Cart empty.');

  const res = await fetch('/api/order', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rfid_card_id: currentCardId, items: cart })
  });
  const data = await res.json();
  if (res.ok) {
    orderMsg.innerText = `Ordered ₹${data.total}. New balance ₹${data.newBalance.toFixed(2)}`;
    currentBalance = data.newBalance;
    cart = [];
    updateQtyDisplay();
  } else {
    orderMsg.innerText = 'Error: ' + (data.error || 'unknown');
  }
});

// ---- Init ----
fetchMenu();
