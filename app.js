document.addEventListener('DOMContentLoaded', () => {
  let fontsData = [];
  let filteredFonts = [];
  let currentPage = 1;
  const pageSize = 36;
  const fontFaceLoaded = new Set();

  let activeCategory = 'all';
  let activeStyle = 'all';
  let searchQuery = '';
  let previewText = 'தமிழ் வாழ்க வளர்க!';
  let fontSize = 32;

  // DOM Elements
  const fontsGrid = document.getElementById('fontsGrid');
  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearch');
  const customTextInput = document.getElementById('customTextInput');
  const presetTextSelect = document.getElementById('presetTextSelect');
  const fontSizeSlider = document.getElementById('fontSizeSlider');
  const fontSizeVal = document.getElementById('fontSizeVal');
  const categorySelect = document.getElementById('categorySelect');
  const styleSelect = document.getElementById('styleSelect');
  const quickSelect = document.getElementById('quickSelect');
  const resetFiltersBtn = document.getElementById('resetFiltersBtn');

  const fontCountMsg = document.getElementById('fontCountMsg');
  const activeFilterMsg = document.getElementById('activeFilterMsg');
  const loadMoreBtn = document.getElementById('loadMoreBtn');
  const gridBtn = document.getElementById('gridBtn');
  const listBtn = document.getElementById('listBtn');
  const themeToggle = document.getElementById('themeToggle');
  const toast = document.getElementById('toast');
  const toastMsg = document.getElementById('toastMsg');
  
  // Modals
  const ccInfoBtn = document.getElementById('ccInfoBtn');
  const licenseModal = document.getElementById('licenseModal');
  const closeModal = document.getElementById('closeModal');
  const modalOkBtn = document.getElementById('modalOkBtn');

  // Load Font Database
  fetch('font_database.json')
    .then(res => res.json())
    .then(data => {
      fontsData = data;
      filteredFonts = data;
      renderApp();
    })
    .catch(err => console.error('Error loading font database:', err));

  function renderApp() {
    applyFilters();
    initLucide();
  }

  function initLucide() {
    if (window.lucide && typeof window.lucide.createIcons === 'function') {
      try {
        window.lucide.createIcons();
      } catch (err) {
        console.warn('Lucide icon initialization note:', err);
      }
    }
  }

  function showToast(message) {
    if (!toast || !toastMsg) return;
    toastMsg.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2500);
  }

  function applyFilters() {
    searchQuery = searchInput ? searchInput.value.toLowerCase().trim() : '';

    filteredFonts = fontsData.filter(f => {
      const matchCat = (activeCategory === 'all') || (f.category === activeCategory);
      const matchStyle = (activeStyle === 'all') || (f.style === activeStyle);
      const matchSearch = !searchQuery || 
        f.name.toLowerCase().includes(searchQuery) || 
        f.filename.toLowerCase().includes(searchQuery) || 
        f.category.toLowerCase().includes(searchQuery);

      return matchCat && matchStyle && matchSearch;
    });

    currentPage = 1;
    updateStatus();
    renderCards(true);
  }

  function updateStatus() {
    if (fontCountMsg) {
      fontCountMsg.innerHTML = `<i data-lucide="file-text" class="status-icon"></i> Showing ${filteredFonts.length.toLocaleString()} of ${fontsData.length.toLocaleString()} fonts`;
    }
    
    let catText = activeCategory === 'all' ? 'All Encodings' : activeCategory;
    let styleText = activeStyle === 'all' ? 'All Styles' : activeStyle;

    if (activeFilterMsg) {
      if (searchQuery) {
        activeFilterMsg.innerHTML = `<i data-lucide="filter" class="status-icon"></i> Search: "${escapeHtml(searchQuery)}" • ${catText} • ${styleText}`;
      } else {
        activeFilterMsg.innerHTML = `<i data-lucide="filter" class="status-icon"></i> Filter: ${catText} • ${styleText}`;
      }
    }

    if (loadMoreBtn) {
      if (currentPage * pageSize >= filteredFonts.length) {
        loadMoreBtn.style.display = 'none';
      } else {
        loadMoreBtn.style.display = 'inline-flex';
      }
    }
  }

  function injectFontFace(font) {
    const fontFamily = `TamilFont_${font.id}`;
    if (!fontFaceLoaded.has(fontFamily)) {
      fontFaceLoaded.add(fontFamily);
      const styleEl = document.createElement('style');
      styleEl.textContent = `
        @font-face {
          font-family: '${fontFamily}';
          src: url('${encodeURI(font.path)}') format('truetype');
          font-display: swap;
        }
      `;
      document.head.appendChild(styleEl);
    }
    return fontFamily;
  }

  function renderCards(reset = false) {
    if (!fontsGrid) return;
    if (reset) {
      fontsGrid.innerHTML = '';
    }

    const startIdx = (currentPage - 1) * pageSize;
    const endIdx = currentPage * pageSize;
    const pageItems = filteredFonts.slice(startIdx, endIdx);

    pageItems.forEach(font => {
      const fontFamily = injectFontFace(font);
      const card = document.createElement('div');
      card.className = 'font-card';
      
      card.innerHTML = `
        <div class="card-header">
          <div class="font-meta">
            <span class="font-name" title="${escapeHtml(font.filename)}">${escapeHtml(font.name)}</span>
            <span class="font-submeta">${escapeHtml(font.category)} • ${escapeHtml(font.size)}</span>
          </div>
          <div class="badge-group">
            <span class="badge" style="background:${font.license_color}">
              <i data-lucide="shield"></i> ${escapeHtml(font.license_badge)}
            </span>
            <span class="badge badge-style">${escapeHtml(font.style)}</span>
          </div>
        </div>

        <div class="font-preview" style="font-family: '${fontFamily}', sans-serif; font-size: ${fontSize}px;">
          ${escapeHtml(previewText || font.sample)}
        </div>

        <div class="card-footer">
          <span class="lic-name" title="${escapeHtml(font.license)}">${escapeHtml(font.license_badge)}</span>
          <div class="btn-group">
            <a href="${encodeURI(font.path)}" download class="action-btn download-btn">
              <i data-lucide="download"></i> Download Font
            </a>
          </div>
        </div>
      `;

      fontsGrid.appendChild(card);
    });

    // Re-initialize Lucide Icons for dynamic content
    initLucide();

    // Attach download toast notification
    document.querySelectorAll('.download-btn').forEach(btn => {
      btn.onclick = () => {
        showToast('Font download started!');
      };
    });
  }

  function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.innerText = text;
    return div.innerHTML;
  }

  // Dropdown Listeners
  if (categorySelect) {
    categorySelect.addEventListener('change', () => {
      activeCategory = categorySelect.value;
      if (quickSelect) quickSelect.value = 'all|all';
      applyFilters();
    });
  }

  if (styleSelect) {
    styleSelect.addEventListener('change', () => {
      activeStyle = styleSelect.value;
      if (quickSelect) quickSelect.value = 'all|all';
      applyFilters();
    });
  }

  if (quickSelect) {
    quickSelect.addEventListener('change', () => {
      const [cat, st] = quickSelect.value.split('|');
      activeCategory = cat || 'all';
      activeStyle = st || 'all';
      if (categorySelect) categorySelect.value = activeCategory;
      if (styleSelect) styleSelect.value = activeStyle;
      applyFilters();
    });
  }

  if (resetFiltersBtn) {
    resetFiltersBtn.addEventListener('click', () => {
      activeCategory = 'all';
      activeStyle = 'all';
      searchQuery = '';
      if (searchInput) searchInput.value = '';
      if (clearSearchBtn) clearSearchBtn.style.display = 'none';
      if (categorySelect) categorySelect.value = 'all';
      if (styleSelect) styleSelect.value = 'all';
      if (quickSelect) quickSelect.value = 'all|all';
      applyFilters();
      showToast('Filters reset to default');
    });
  }

  // Search & Input Listeners
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      if (clearSearchBtn) clearSearchBtn.style.display = searchInput.value ? 'flex' : 'none';
      applyFilters();
    });
  }

  if (clearSearchBtn) {
    clearSearchBtn.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      clearSearchBtn.style.display = 'none';
      applyFilters();
    });
  }

  if (customTextInput) {
    customTextInput.addEventListener('input', () => {
      previewText = customTextInput.value;
      updatePreviews();
    });
  }

  if (presetTextSelect) {
    presetTextSelect.addEventListener('change', () => {
      if (customTextInput) customTextInput.value = presetTextSelect.value;
      previewText = presetTextSelect.value;
      updatePreviews();
    });
  }

  if (fontSizeSlider) {
    fontSizeSlider.addEventListener('input', () => {
      fontSize = fontSizeSlider.value;
      if (fontSizeVal) fontSizeVal.textContent = `${fontSize}px`;
      updatePreviews();
    });
  }

  function updatePreviews() {
    document.querySelectorAll('.font-preview').forEach(prev => {
      prev.style.fontSize = `${fontSize}px`;
      prev.innerText = previewText || 'தமிழ் வாழ்க வளர்க!';
    });
  }

  // View Toggle
  if (gridBtn && listBtn && fontsGrid) {
    gridBtn.addEventListener('click', () => {
      gridBtn.classList.add('active-view-btn');
      listBtn.classList.remove('active-view-btn');
      fontsGrid.classList.remove('list-view');
    });

    listBtn.addEventListener('click', () => {
      listBtn.classList.add('active-view-btn');
      gridBtn.classList.remove('active-view-btn');
      fontsGrid.classList.add('list-view');
    });
  }

  // Theme Toggle
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      document.documentElement.classList.toggle('dark');
      document.documentElement.classList.toggle('light');
      initLucide();
    });
  }

  // Load More
  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', () => {
      currentPage++;
      updateStatus();
      renderCards(false);
    });
  }

  // Modals
  if (ccInfoBtn && licenseModal) {
    ccInfoBtn.onclick = () => {
      licenseModal.classList.add('active');
      initLucide();
    };
  }

  if (closeModal && licenseModal) {
    closeModal.onclick = () => licenseModal.classList.remove('active');
  }

  if (modalOkBtn && licenseModal) {
    modalOkBtn.onclick = () => licenseModal.classList.remove('active');
  }

  window.onclick = (e) => {
    if (licenseModal && e.target === licenseModal) {
      licenseModal.classList.remove('active');
    }
  };
});
