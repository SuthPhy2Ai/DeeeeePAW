(function () {
  function insertSwitcher() {
    var path = window.location.pathname;
    var targetHref = null;
    var label = null;

    if (path.indexOf('/zh_CN/') !== -1) {
      targetHref = path.replace('/zh_CN/', '/en/');
      label = 'English';
    } else if (path.indexOf('/en/') !== -1) {
      targetHref = path.replace('/en/', '/zh_CN/');
      label = 'Chinese';
    } else {
      return;
    }

    var searchBox = document.querySelector('.wy-side-nav-search');
    if (searchBox && !searchBox.querySelector('.language-switcher')) {
      var desktopLink = document.createElement('a');
      desktopLink.className = 'language-switcher';
      desktopLink.href = targetHref;
      desktopLink.textContent = label;
      searchBox.appendChild(desktopLink);
    }

    var mobileNav = document.querySelector('.wy-nav-top');
    if (mobileNav && !mobileNav.querySelector('.language-switcher-mobile')) {
      var mobileLink = document.createElement('a');
      mobileLink.className = 'language-switcher-mobile';
      mobileLink.href = targetHref;
      mobileLink.textContent = label;
      mobileNav.appendChild(mobileLink);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', insertSwitcher);
  } else {
    insertSwitcher();
  }
})();
