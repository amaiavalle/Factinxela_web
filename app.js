document.documentElement.classList.add("js");

const header = document.querySelector("[data-header]");
const nav = document.querySelector("[data-nav]");
const navToggle = document.querySelector("[data-nav-toggle]");

const updateHeader = () => {
  header?.classList.toggle("scrolled", window.scrollY > 18);
};

updateHeader();
window.addEventListener("scroll", updateHeader, { passive: true });

const closeNavigation = () => {
  if (!nav || !navToggle) return;
  nav.classList.remove("open");
  navToggle.setAttribute("aria-expanded", "false");
  document.body.classList.remove("nav-open");
};

navToggle?.addEventListener("click", () => {
  const opening = navToggle.getAttribute("aria-expanded") !== "true";
  nav?.classList.toggle("open", opening);
  navToggle.setAttribute("aria-expanded", String(opening));
  document.body.classList.toggle("nav-open", opening);
});

nav?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", closeNavigation);
});

window.addEventListener("resize", () => {
  if (window.innerWidth > 900) closeNavigation();
});

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const revealItems = document.querySelectorAll(".reveal");

if (reducedMotion || !("IntersectionObserver" in window)) {
  revealItems.forEach((item) => item.classList.add("visible"));
} else {
  const observer = new IntersectionObserver((entries, activeObserver) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("visible");
      activeObserver.unobserve(entry.target);
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -45px" });

  revealItems.forEach((item) => observer.observe(item));
}

const lightbox = document.querySelector("[data-lightbox-dialog]");
const lightboxImage = document.querySelector("[data-lightbox-image]");
const lightboxCaption = document.querySelector("[data-lightbox-caption]");
const lightboxClose = document.querySelector("[data-lightbox-close]");

const closeLightbox = () => {
  if (!lightbox?.open) return;
  lightbox.close();
};

document.querySelectorAll("[data-lightbox]").forEach((trigger) => {
  trigger.addEventListener("click", () => {
    if (!lightbox || !lightboxImage || typeof lightbox.showModal !== "function") {
      window.open(trigger.dataset.lightbox, "_blank", "noopener");
      return;
    }

    const sourceImage = trigger.querySelector("img");
    const figureCaption = trigger.closest("figure")?.querySelector("figcaption");
    lightboxImage.src = trigger.dataset.lightbox;
    lightboxImage.alt = sourceImage?.alt || "Captura ampliada de Factinxela";
    lightboxCaption.textContent = figureCaption?.textContent.trim() || sourceImage?.alt || "";
    lightbox.showModal();
    document.body.classList.add("lightbox-open");
  });
});

lightboxClose?.addEventListener("click", closeLightbox);

lightbox?.addEventListener("click", (event) => {
  const bounds = lightbox.getBoundingClientRect();
  const outside = event.clientX < bounds.left || event.clientX > bounds.right
    || event.clientY < bounds.top || event.clientY > bounds.bottom;
  if (outside) closeLightbox();
});

lightbox?.addEventListener("close", () => {
  document.body.classList.remove("lightbox-open");
  if (lightboxImage) lightboxImage.src = "";
});

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  closeNavigation();
  closeLightbox();
});

const year = String(new Date().getFullYear());
document.querySelectorAll("[data-year]").forEach((element) => {
  element.textContent = year;
});
