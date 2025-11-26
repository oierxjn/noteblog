// Aurora Theme JavaScript
// 极光主题交互功能

class AuroraTheme {
    constructor() {
        this.init();
    }

    init() {
        this.initThemeToggle();
        this.initScrollEffects();
        this.initBackToTop();
        this.initNavigation();
        this.initAnimations();
        this.initSearch();
        this.initAuthModals();
        this.initComments();
        this.initImageLazyLoad();
        this.initDarkMode();
    }

    // 主题切换功能
    initThemeToggle() {
        const themeToggle = document.querySelector('.theme-toggle');
        if (!themeToggle) return;

        // 检查本地存储的主题设置
        const savedTheme = localStorage.getItem('aurora-theme') || 'light';
        this.setTheme(savedTheme);

        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            this.setTheme(newTheme);
            localStorage.setItem('aurora-theme', newTheme);
        });
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.innerHTML = theme === 'dark' ? '☀️' : '🌙';
        }
    }

    // 滚动效果
    initScrollEffects() {
        const header = document.querySelector('.site-header');
        if (!header) return;

        let lastScrollY = window.scrollY;
        let ticking = false;

        const updateHeader = () => {
            const scrollY = window.scrollY;
            
            if (scrollY > 100) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }

            lastScrollY = scrollY;
            ticking = false;
        };

        const requestTick = () => {
            if (!ticking) {
                requestAnimationFrame(updateHeader);
                ticking = true;
            }
        };

        window.addEventListener('scroll', requestTick, { passive: true });
    }

    // 返回顶部按钮
    initBackToTop() {
        const backToTop = document.querySelector('.back-to-top');
        if (!backToTop) return;

        const toggleBackToTop = () => {
            if (window.scrollY > 300) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        };

        backToTop.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        window.addEventListener('scroll', toggleBackToTop, { passive: true });
        toggleBackToTop();
    }

    // 导航功能
    initNavigation() {
        const navItems = document.querySelectorAll('.aurora-nav-item');
        const currentPath = window.location.pathname;

        navItems.forEach(item => {
            const href = item.getAttribute('href');
            if (href && (href === currentPath || (href === '/' && currentPath === ''))) {
                item.classList.add('active');
            }

            item.addEventListener('click', (e) => {
                // 移除所有active类
                navItems.forEach(nav => nav.classList.remove('active'));
                // 添加active类到当前项
                item.classList.add('active');
            });
        });

        // 移动端导航切换
        this.initMobileNavigation();
    }

    initMobileNavigation() {
        const mobileToggle = document.querySelector('.mobile-nav-toggle');
        const nav = document.querySelector('.main-navigation');
        
        if (!mobileToggle || !nav) return;

        mobileToggle.addEventListener('click', () => {
            nav.classList.toggle('mobile-open');
            mobileToggle.classList.toggle('active');
        });

        // 点击外部关闭移动导航
        document.addEventListener('click', (e) => {
            if (!nav.contains(e.target) && !mobileToggle.contains(e.target)) {
                nav.classList.remove('mobile-open');
                mobileToggle.classList.remove('active');
            }
        });
    }

    // 动画效果
    initAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // 观察需要动画的元素
        const animatedElements = document.querySelectorAll('.post-item, .widget, .fade-in-up');
        animatedElements.forEach(el => observer.observe(el));
    }

    // 搜索功能
    initSearch() {
        const searchToggle = document.querySelector('.search-toggle');
        const searchModal = document.querySelector('.search-modal');
        const searchInput = document.querySelector('.search-input');
        const searchClose = document.querySelector('.search-close');

        if (!searchToggle || !searchModal) return;

        const toggleSearchModal = (shouldOpen) => {
            searchModal.classList.toggle('active', shouldOpen);
            searchModal.setAttribute('aria-hidden', (!shouldOpen).toString());
            document.body.classList.toggle('search-open', shouldOpen);

            if (shouldOpen && searchInput) {
                setTimeout(() => searchInput.focus(), 100);
            }
        };

        searchToggle.addEventListener('click', () => toggleSearchModal(true));

        if (searchClose) {
            searchClose.addEventListener('click', () => toggleSearchModal(false));
        }

        // ESC键关闭搜索
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && searchModal.classList.contains('active')) {
                toggleSearchModal(false);
            }
        });

        // 点击背景关闭搜索
        searchModal.addEventListener('click', (e) => {
            if (e.target === searchModal) {
                toggleSearchModal(false);
            }
        });
    }

    // 认证模态框
    initAuthModals() {
        const modals = document.querySelectorAll('.auth-modal');
        if (!modals.length) return;

        const modalMap = {};
        modals.forEach(modal => {
            const key = modal.dataset.modal;
            if (key) {
                modalMap[key] = modal;
            }
        });

        const body = document.body;
        let activeModal = null;

        const updateModalQuery = (value) => {
            try {
                const url = new URL(window.location.href);
                if (value) {
                    url.searchParams.set('modal', value);
                } else {
                    url.searchParams.delete('modal');
                }
                window.history.replaceState({}, '', url);
            } catch (error) {
                console.warn('更新 modal 查询参数失败', error);
            }
        };

        const closeAllModals = () => {
            Object.values(modalMap).forEach(modal => {
                modal.classList.remove('active');
                modal.setAttribute('aria-hidden', 'true');
            });
            body.classList.remove('modal-open');
            activeModal = null;
            updateModalQuery(null);
        };

        const openModal = (name) => {
            const modal = modalMap[name];
            if (!modal) return;

            Object.entries(modalMap).forEach(([key, value]) => {
                if (key !== name) {
                    value.classList.remove('active');
                    value.setAttribute('aria-hidden', 'true');
                }
            });

            modal.classList.add('active');
            modal.setAttribute('aria-hidden', 'false');
            body.classList.add('modal-open');
            activeModal = name;
            updateModalQuery(name);

            const firstField = modal.querySelector('input, textarea, select, button');
            if (firstField) {
                setTimeout(() => firstField.focus(), 120);
            }
        };

        document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
            trigger.addEventListener('click', (event) => {
                event.preventDefault();
                const target = trigger.dataset.modalTrigger;
                if (target) {
                    openModal(target);
                }
            });
        });

        document.querySelectorAll('[data-modal-close]').forEach(button => {
            button.addEventListener('click', () => closeAllModals());
        });

        document.querySelectorAll('[data-modal-switch]').forEach(button => {
            button.addEventListener('click', (event) => {
                event.preventDefault();
                const target = button.dataset.modalSwitch;
                if (target) {
                    openModal(target);
                }
            });
        });

        Object.values(modalMap).forEach(modal => {
            modal.addEventListener('click', (event) => {
                if (event.target === modal) {
                    closeAllModals();
                }
            });
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && activeModal) {
                closeAllModals();
            }
        });

        // 根据 URL 参数自动打开对应模态框
        try {
            const params = new URLSearchParams(window.location.search);
            const initialModal = params.get('modal');
            if (initialModal && modalMap[initialModal]) {
                openModal(initialModal);
            }
        } catch (error) {
            console.warn('解析 modal 查询参数失败', error);
        }
    }

    // 评论功能
    initComments() {
        this.initCommentForm();
        this.initCommentReply();
        this.initCommentEdit();
    }

    initCommentForm() {
        const commentForm = document.querySelector('.comment-form');
        if (!commentForm) return;

        commentForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const submitBtn = commentForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            // 显示加载状态
            submitBtn.disabled = true;
            submitBtn.textContent = '提交中...';
            
            // 模拟提交
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
                this.showNotification('评论提交成功！', 'success');
                commentForm.reset();
            }, 1500);
        });
    }

    initCommentReply() {
        const replyButtons = document.querySelectorAll('.reply-btn');
        replyButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const commentId = btn.dataset.commentId;
                const authorName = btn.dataset.authorName;
                const replyForm = document.querySelector('.reply-form');
                
                if (replyForm) {
                    replyForm.classList.remove('hidden');
                    const replyInput = replyForm.querySelector('textarea');
                    if (replyInput) {
                        replyInput.value = `@${authorName} `;
                        replyInput.focus();
                    }
                }
            });
        });
    }

    initCommentEdit() {
        const editButtons = document.querySelectorAll('.edit-comment-btn');
        editButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const commentId = btn.dataset.commentId;
                const commentText = btn.dataset.commentText;
                const commentContent = document.querySelector(`.comment-content[data-comment-id="${commentId}"]`);
                
                if (commentContent) {
                    const currentText = commentContent.textContent.trim();
                    const textarea = document.createElement('textarea');
                    textarea.value = currentText;
                    textarea.className = 'comment-edit-textarea';
                    
                    const saveBtn = document.createElement('button');
                    saveBtn.textContent = '保存';
                    saveBtn.className = 'comment-save-btn';
                    
                    const cancelBtn = document.createElement('button');
                    cancelBtn.textContent = '取消';
                    cancelBtn.className = 'comment-cancel-btn';
                    
                    commentContent.innerHTML = '';
                    commentContent.appendChild(textarea);
                    commentContent.appendChild(saveBtn);
                    commentContent.appendChild(cancelBtn);
                    
                    textarea.focus();
                    
                    const saveEdit = () => {
                        commentContent.textContent = textarea.value;
                        this.showNotification('评论已更新', 'success');
                    };
                    
                    const cancelEdit = () => {
                        commentContent.textContent = currentText;
                    };
                    
                    saveBtn.addEventListener('click', saveEdit);
                    cancelBtn.addEventListener('click', cancelEdit);
                }
            });
        });
    }

    // 图片懒加载
    initImageLazyLoad() {
        const imageOptions = {
            threshold: 0,
            rootMargin: '50px'
        };

        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.dataset.src;
                    if (src) {
                        img.src = src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                }
            });
        }, imageOptions);

        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => imageObserver.observe(img));
    }

    // 深色模式增强
    initDarkMode() {
        // 检查系统主题偏好
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
        
        const handleThemeChange = (e) => {
            if (!localStorage.getItem('aurora-theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        };

        prefersDark.addEventListener('change', handleThemeChange);
        
        // 初始检查
        if (!localStorage.getItem('aurora-theme')) {
            this.setTheme(prefersDark.matches ? 'dark' : 'light');
        }
    }

    // 通知功能
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `aurora-notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // 显示动画
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // 自动隐藏
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // 工具方法
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // 平滑滚动到元素
    scrollToElement(element, offset = 0) {
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }

    // 格式化日期
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 30) {
            return date.toLocaleDateString('zh-CN');
        } else if (days > 0) {
            return `${days}天前`;
        } else if (hours > 0) {
            return `${hours}小时前`;
        } else if (minutes > 0) {
            return `${minutes}分钟前`;
        } else {
            return '刚刚';
        }
    }

    // 复制到剪贴板
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showNotification('已复制到剪贴板', 'success');
        } catch (err) {
            // 降级方案
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showNotification('已复制到剪贴板', 'success');
        }
    }
}

// 初始化主题
document.addEventListener('DOMContentLoaded', () => {
    window.auroraTheme = new AuroraTheme();
});

// 导出给全局使用
window.AuroraTheme = AuroraTheme;
