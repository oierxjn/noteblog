(function () {
  const doc = document;
  const root = doc.documentElement;
  const body = doc.body;
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
  let toastTimer;
  const navToggle = doc.querySelector('[data-hoshi-nav-toggle]');
  const nav = doc.querySelector('[data-hoshi-nav]');
  const searchToggle = doc.querySelectorAll('[data-hoshi-search]');
  const searchOverlay = doc.querySelector('[data-hoshi-search-overlay]');
  const searchClose = doc.querySelector('[data-hoshi-search-close]');
  const themeToggle = doc.querySelector('[data-hoshi-theme]');
  const backToTop = doc.querySelector('[data-hoshi-backtotop]');
  const progressBar = doc.querySelector('[data-hoshi-progress]');
  const authToggles = doc.querySelectorAll('[data-hoshi-auth-toggle]');
  const authModal = doc.querySelector('[data-hoshi-auth-modal]');
  const authClose = doc.querySelectorAll('[data-hoshi-auth-close]');
  const particleCanvas = doc.querySelector('[data-hoshi-particles]');
  const commentForm = doc.querySelector('.hoshi-comment-form');

  function showToast(message, type = 'info') {
    let toast = doc.querySelector('.hoshi-toast');
    if (!toast) {
      toast = doc.createElement('div');
      toast.className = 'hoshi-toast';
      doc.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.dataset.type = type;
    toast.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('visible'), 2800);
  }

  async function postJson(url, payload) {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || '请求失败');
    }
    return response.json().catch(() => ({}));
  }

  function toggleNav() {
    if (!nav) return;
    nav.classList.toggle('open');
  }

  function openSearch() {
    if (!searchOverlay) return;
    searchOverlay.classList.add('active');
    const input = searchOverlay.querySelector('input');
    setTimeout(() => input && input.focus(), 60);
  }

  function closeSearch() {
    if (!searchOverlay) return;
    searchOverlay.classList.remove('active');
  }

  function openAuth(target) {
    if (!authModal) return;
    authModal.dataset.modal = target || 'login';
    authModal.classList.add('active');
    const panels = authModal.querySelectorAll('[data-hoshi-auth-panel]');
    panels.forEach((panel) => {
      panel.style.display = panel.dataset.hoshiAuthPanel === (target || 'login') ? 'block' : 'none';
    });
    const input = authModal.querySelector('[data-hoshi-auth-input="' + (target || 'login') + '"]');
    setTimeout(() => input && input.focus(), 80);
  }

  function closeAuth() {
    if (!authModal) return;
    authModal.classList.remove('active');
  }

  function handleScroll() {
    const scrolled = window.scrollY;
    if (backToTop) {
      if (scrolled > 280) {
        backToTop.classList.add('visible');
      } else {
        backToTop.classList.remove('visible');
      }
    }
    if (progressBar) {
      const height = body.scrollHeight - window.innerHeight;
      const progress = height > 0 ? Math.min((scrolled / height) * 100, 100) : 0;
      progressBar.style.setProperty('--hoshi-progress', progress + '%');
      progressBar.querySelector('span').style.width = progress + '%';
    }
  }

  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function resolveInitialTheme() {
    const stored = localStorage.getItem('hoshizora-theme');
    if (stored) return stored;
    if (body.dataset.defaultMode) return body.dataset.defaultMode;
    return prefersDark.matches ? 'dark' : 'light';
  }

  function applyTheme(mode) {
    root.setAttribute('data-theme', mode);
    body.dataset.currentMode = mode;
  }

  function toggleTheme() {
    const next = body.dataset.currentMode === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    localStorage.setItem('hoshizora-theme', next);
  }

  function bindNav() {
    if (!navToggle) return;
    navToggle.addEventListener('click', toggleNav);
  }

  function bindSearch() {
    searchToggle.forEach((btn) => btn.addEventListener('click', openSearch));
    if (searchClose) searchClose.addEventListener('click', closeSearch);
    doc.addEventListener('keydown', (evt) => {
      if (evt.key === 'Escape') {
        closeSearch();
        closeAuth();
      }
      if (evt.key.toLowerCase() === 'k' && evt.metaKey || evt.ctrlKey && evt.key.toLowerCase() === 'k') {
        evt.preventDefault();
        openSearch();
      }
    });
    if (searchOverlay) {
      searchOverlay.addEventListener('click', (evt) => {
        if (evt.target === searchOverlay) closeSearch();
      });
    }
  }

  function bindAuth() {
    authToggles.forEach((btn) => {
      btn.addEventListener('click', () => openAuth(btn.dataset.hoshiAuthToggle));
    });
    authClose.forEach((btn) => btn.addEventListener('click', closeAuth));
    if (authModal) {
      authModal.addEventListener('click', (evt) => {
        if (evt.target === authModal) closeAuth();
      });
    }
  }

  function bindThemeToggle() {
    if (!themeToggle) return;
    themeToggle.addEventListener('click', toggleTheme);
  }

  function bindBackToTop() {
    if (!backToTop) return;
    backToTop.addEventListener('click', scrollToTop);
  }

  function bindCopyButtons() {
    doc.querySelectorAll('[data-hoshi-copy]').forEach((btn) => {
      if (btn.dataset.copyBound) return;
      btn.dataset.copyBound = '1';
      btn.addEventListener('click', async () => {
        const text = btn.dataset.copyValue || btn.textContent.trim() || window.location.href;
        try {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(text);
          } else {
            const textarea = doc.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            doc.body.appendChild(textarea);
            textarea.select();
            doc.execCommand('copy');
            textarea.remove();
          }
          showToast('链接已复制');
        } catch (error) {
          showToast('复制失败，请手动复制', 'error');
        }
      });
    });
  }

  function updatePostLikeButtons(postId, liked, count) {
    doc.querySelectorAll(`[data-hoshi-like-post][data-post-id="${postId}"]`).forEach((button) => {
      button.dataset.liked = liked ? 'true' : 'false';
      const counter = button.querySelector('[data-like-count]');
      if (counter && typeof count === 'number') {
        counter.textContent = count;
      }
      button.classList.toggle('liked', liked);
    });
  }

  function bindPostLikeButtons() {
    doc.querySelectorAll('[data-hoshi-like-post]').forEach((button) => {
      if (button.dataset.likeBound) return;
      button.dataset.likeBound = '1';
      button.addEventListener('click', async () => {
        const postId = Number(button.dataset.postId);
        if (!postId || button.dataset.likeProcessing === '1') return;
        const liked = button.dataset.liked === 'true';
        button.dataset.likeProcessing = '1';
        button.disabled = true;
        try {
          const result = await postJson(`/api/posts/${postId}/like`, {
            action: liked ? 'unlike' : 'like',
          });
          const nextLiked = result?.data?.liked ?? !liked;
          const likeCount = result?.data?.like_count ?? result?.data?.likeCount;
          updatePostLikeButtons(postId, nextLiked, likeCount);
          showToast(result?.message || (nextLiked ? '已加入喜欢' : '已取消喜欢'));
        } catch (error) {
          showToast(error.message || '操作失败', 'error');
        } finally {
          button.dataset.likeProcessing = '0';
          button.disabled = false;
        }
      });
    });
  }

  function updateCommentLikeButtons(commentId, liked, count) {
    doc.querySelectorAll(`[data-hoshi-comment-like][data-comment-id="${commentId}"]`).forEach((button) => {
      button.dataset.liked = liked ? 'true' : 'false';
      const counter = button.querySelector('[data-like-count]');
      if (counter && typeof count === 'number') {
        counter.textContent = count;
      }
      button.classList.toggle('liked', liked);
    });
  }

  function bindCommentLikeButtons() {
    doc.querySelectorAll('[data-hoshi-comment-like]').forEach((button) => {
      if (button.dataset.likeBound) return;
      button.dataset.likeBound = '1';
      button.addEventListener('click', async () => {
        const commentId = Number(button.dataset.commentId);
        if (!commentId || button.dataset.likeProcessing === '1') return;
        const liked = button.dataset.liked === 'true';
        button.dataset.likeProcessing = '1';
        button.disabled = true;
        try {
          const result = await postJson(`/api/comments/${commentId}/like`, {
            action: liked ? 'unlike' : 'like',
          });
          const nextLiked = result?.data?.liked ?? !liked;
          const likeCount = result?.data?.like_count ?? result?.data?.likeCount;
          updateCommentLikeButtons(commentId, nextLiked, likeCount);
          showToast(result?.message || (nextLiked ? '已点赞评论' : '已取消点赞'));
        } catch (error) {
          showToast(error.message || '操作失败', 'error');
        } finally {
          button.dataset.likeProcessing = '0';
          button.disabled = false;
        }
      });
    });
  }

  function initCommentForm() {
    if (!commentForm) return;
    const parentInput = commentForm.querySelector('input[name="parent_id"]');
    const indicator = commentForm.querySelector('[data-reply-indicator]');
    const replyNameTarget = commentForm.querySelector('[data-reply-name]');
    const cancelBtn = commentForm.querySelector('[data-cancel-reply]');
    const textarea = commentForm.querySelector('textarea[name="content"]');

    const toggleReply = (active, author) => {
      if (!indicator) return;
      if (active) {
        indicator.hidden = false;
        if (replyNameTarget) replyNameTarget.textContent = author || '';
      } else {
        indicator.hidden = true;
        if (replyNameTarget) replyNameTarget.textContent = '';
      }
    };

    const clearReply = () => {
      if (parentInput) parentInput.value = '';
      toggleReply(false);
    };

    const bindReplyButtons = () => {
      doc.querySelectorAll('[data-hoshi-reply]').forEach((button) => {
        if (button.dataset.replyBound) return;
        button.dataset.replyBound = '1';
        button.addEventListener('click', () => {
          if (!parentInput) return;
          parentInput.value = button.dataset.commentId || '';
          toggleReply(true, button.dataset.author || '');
          if (textarea) {
            textarea.focus();
            const mention = `@${button.dataset.author || ''} `;
            if (!textarea.value.trim()) {
              textarea.value = mention;
            }
            if (typeof textarea.setSelectionRange === 'function') {
              const len = textarea.value.length;
              textarea.setSelectionRange(len, len);
            }
          }
        });
      });
    };

    bindReplyButtons();
    cancelBtn?.addEventListener('click', (event) => {
      event.preventDefault();
      clearReply();
    });

    commentForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const submit = commentForm.querySelector('button[type="submit"]');
      if (submit) {
        submit.disabled = true;
        submit.textContent = '发送中...';
      }
      try {
        const payload = Object.fromEntries(new FormData(commentForm).entries());
        const result = await postJson('/api/comments', payload);
        showToast(result?.message || '评论已提交');
        commentForm.reset();
        clearReply();
        window.location.reload();
      } catch (error) {
        showToast(error.message || '提交失败', 'error');
      } finally {
        if (submit) {
          submit.disabled = false;
          submit.textContent = '提交评论';
        }
      }
    });
  }

  function initParticles() {
    if (!particleCanvas || body.dataset.particles !== 'true') return;
    const canvas = particleCanvas;
    const ctx = canvas.getContext('2d');
    const particles = new Array(80).fill(0).map(() => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      r: Math.random() * 1.8 + 0.4,
      vx: (Math.random() - 0.5) * 0.2,
      vy: (Math.random() - 0.5) * 0.2,
    }));

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = 'rgba(255,255,255,0.85)';
      particles.forEach((p) => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;
      });
      requestAnimationFrame(draw);
    };

    resize();
    draw();
    window.addEventListener('resize', resize);
  }

  function initParallax() {
    if (body.dataset.parallax !== 'true') return;
    const hero = doc.querySelector('.hoshi-hero');
    if (!hero) return;
    const handle = (evt) => {
      const rect = hero.getBoundingClientRect();
      const relX = (evt.clientX - rect.left) / rect.width - 0.5;
      const relY = (evt.clientY - rect.top) / rect.height - 0.5;
      hero.style.setProperty('--parallax-x', relX * 12 + 'px');
      hero.style.setProperty('--parallax-y', relY * 12 + 'px');
    };
    hero.addEventListener('mousemove', handle);
  }

  function init() {
    bindNav();
    bindSearch();
    bindAuth();
    bindThemeToggle();
    bindBackToTop();
    bindCopyButtons();
    bindPostLikeButtons();
    bindCommentLikeButtons();
    initCommentForm();
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    const initialTheme = resolveInitialTheme();
    applyTheme(initialTheme);
    initParticles();
    initParallax();
  }

  doc.addEventListener('DOMContentLoaded', init);
})();
