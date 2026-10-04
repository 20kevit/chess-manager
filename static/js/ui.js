/**
 * ui.js — unified frontend interactions (design system).
 * - theme toggle (light/dark, persisted)
 * - mobile drawer + sidebar drawer (focus trap-lite, ESC, overlay)
 * - accessible confirm dialog replacing native confirm()
 * - alert dismissal delegation, toast helper
 * No business logic. Vanilla only.
 */
(function () {
  "use strict";

  /* ---------- theme ---------- */
  function initTheme() {
    var btn = document.getElementById("themeToggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var root = document.documentElement;
      var next = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      try { localStorage.setItem("cm-theme", next); } catch (e) {}
      btn.setAttribute("aria-label", next === "dark" ? "تغییر به تم روشن" : "تغییر به تم تیره");
    });
  }

  /* ---------- drawer (mobile nav + sidebar) ---------- */
  function trapTab(container, e) {
    var items = container.querySelectorAll('a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (!items.length) return;
    var first = items[0], last = items[items.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  function initDrawer(toggleId, drawerId, scrimId, closeId) {
    var toggle = document.getElementById(toggleId);
    var drawer = document.getElementById(drawerId);
    if (!toggle || !drawer) return;
    var scrim = scrimId ? document.getElementById(scrimId) : null;
    var closeBtn = closeId ? document.getElementById(closeId) : null;
    var lastFocus = null;

    function open() {
      lastFocus = document.activeElement;
      drawer.classList.add("open");
      drawer.setAttribute("aria-hidden", "false");
      toggle.setAttribute("aria-expanded", "true");
      if (scrim) scrim.classList.add("open");
      document.body.style.overflow = "hidden";
      var f = drawer.querySelector("a[href], button:not([disabled])");
      if (f) f.focus();
    }
    function close(restore) {
      drawer.classList.remove("open");
      drawer.setAttribute("aria-hidden", "true");
      toggle.setAttribute("aria-expanded", "false");
      if (scrim) scrim.classList.remove("open");
      document.body.style.overflow = "";
      if (restore !== false && lastFocus && lastFocus.focus) lastFocus.focus();
    }
    toggle.addEventListener("click", function () {
      drawer.classList.contains("open") ? close() : open();
    });
    if (closeBtn) closeBtn.addEventListener("click", function () { close(); });
    if (scrim) scrim.addEventListener("click", function () { close(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && drawer.classList.contains("open")) close();
      if (e.key === "Tab" && drawer.classList.contains("open")) trapTab(drawer, e);
    });
  }

  function initSidebarToggle() {
    var t = document.getElementById("adminSidebarToggle");
    var s = document.getElementById("adminSidebar");
    if (!t || !s) return;
    t.addEventListener("click", function () {
      var open = s.classList.toggle("open");
      t.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && s.classList.contains("open")) {
        s.classList.remove("open");
        t.setAttribute("aria-expanded", "false");
        t.focus();
      }
    });
  }

  /* ---------- accessible confirm (replaces native confirm()) ----------
     Usage on links/buttons:  data-confirm="متن پیام" [data-confirm-hint="..."]
     Usage on forms:           same attributes on the <form> element.
     On confirm: links navigate, buttons submit parent form, forms submit. */
  var pending = null;

  function dialog() { return document.getElementById("confirmDialog"); }
  function openConfirm(opts) {
    var d = dialog();
    if (!d) { // fallback: proceed only for non-destructive? ask via native as last resort
      if (window.confirm(opts.body)) opts.onConfirm();
      return;
    }
    d.querySelector("#confirmTitle").textContent = opts.title || "آیا مطمئن هستید؟";
    d.querySelector("#confirmBody").textContent = opts.body || "";
    d.querySelector("#confirmHint").textContent = opts.hint || "این عمل ممکن است قابل بازگشت نباشد.";
    d.style.display = "flex";
    d.classList.add("active");
    document.body.style.overflow = "hidden";
    pending = opts;
    var yes = d.querySelector("#confirmYes");
    if (yes) yes.focus();
  }
  function closeConfirm() {
    var d = dialog();
    if (!d) return;
    d.classList.remove("active");
    d.style.display = "none";
    document.body.style.overflow = "";
    pending = null;
  }

  function initConfirm() {
    var d = dialog();
    if (d) {
      d.querySelector("#confirmNo").addEventListener("click", closeConfirm);
      d.querySelector("#confirmYes").addEventListener("click", function () {
        var op = pending;
        closeConfirm();
        if (op && op.onConfirm) op.onConfirm();
      });
      d.addEventListener("click", function (e) {
        if (e.target === d) closeConfirm();
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && pending) closeConfirm();
        if (e.key === "Tab" && pending) trapTab(d, e);
      });
    }

    // links & buttons (forms own their dialog via the submit handler below)
    document.querySelectorAll("[data-confirm]").forEach(function (el) {
      if (el.tagName === "FORM") return;
      el.addEventListener("click", function (e) {
        if (el.closest("form[data-confirm]")) return; // form handler owns it
        e.preventDefault();
        e.stopPropagation();
        var target = el;
        openConfirm({
          title: target.getAttribute("data-confirm-title") || "آیا مطمئن هستید؟",
          body: target.getAttribute("data-confirm"),
          hint: target.getAttribute("data-confirm-hint") || "",
          onConfirm: function () {
            if (target.tagName === "A" && target.href) { window.location.href = target.href; return; }
            var form = target.closest("form") || target.form;
            if (form) {
              if (typeof form.requestSubmit === "function") form.requestSubmit();
              else form.submit();
            }
          }
        });
      });
    });

    // forms (capture: runs before app.js double-submit, fine)
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        if (form.dataset.confirmed === "1") { delete form.dataset.confirmed; return; }
        e.preventDefault();
        e.stopImmediatePropagation();
        openConfirm({
          title: form.getAttribute("data-confirm-title") || "آیا مطمئن هستید؟",
          body: form.getAttribute("data-confirm"),
          hint: form.getAttribute("data-confirm-hint") || "",
          onConfirm: function () {
            form.dataset.confirmed = "1";
            // requestSubmit preserves validation + submit listeners
            // (e.g. double-submit protection); fallback to submit().
            if (typeof form.requestSubmit === "function") form.requestSubmit();
            else form.submit();
          }
        });
      }, true);
    });
  }

  /* ---------- alerts + toast ---------- */
  function initAlerts() {
    document.addEventListener("click", function (e) {
      var btn = e.target.closest ? e.target.closest(".alert-close") : null;
      if (!btn) return;
      var alert = btn.closest(".alert");
      if (alert) alert.remove();
    });
  }

  function toast(message) {
    var region = document.getElementById("toastRegion");
    if (!region) return;
    var t = document.createElement("div");
    t.className = "toast";
    t.textContent = message;
    region.appendChild(t);
    setTimeout(function () { t.remove(); }, 3500);
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTheme();
    initDrawer("navToggle", "mobileDrawer", "drawerScrim", "drawerClose");
    initSidebarToggle();
    initConfirm();
    initAlerts();
  });

  window.UI = { toast: toast, openConfirm: openConfirm, closeConfirm: closeConfirm };
})();
