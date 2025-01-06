const container = document.querySelector('.container'); // Pilih satu elemen container
const registerBtn = document.querySelector('.register-btn'); // Pilih tombol register
const loginBtn = document.querySelector('.login-btn'); // Pilih tombol login

// Tambahkan event listener untuk tombol register
registerBtn.addEventListener('click', () => {
    container.classList.add('active'); // Tambahkan class 'active'
});

// Tambahkan event listener untuk tombol login
loginBtn.addEventListener('click', () => {
    container.classList.remove('active'); // Hapus class 'active'
});