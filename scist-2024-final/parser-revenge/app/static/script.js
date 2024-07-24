ComponentIndex = {
  SCHEME: 1,
  USER_INFO: 2,
  DOMAIN: 3,
  PORT: 4,
  PATH: 5,
  QUERY_DATA: 6,
  FRAGMENT: 7,
};

async function buildUrl(url) {
  splitRe_ = RegExp(
    "^(?:([^:/?#.]+):)?(?://(?:([^\\\\/?#]*)@)?([^\\\\/?#]*?)(?::([0-9]+))?(?=[\\\\/?#]|$))?([^?#]+)?(?:\\?([^#]*))?(?:#([\\s\\S]*))?$",
  );
  tmp = url.match(splitRe_);
  scheme = decodeURIComponent(tmp[ComponentIndex.SCHEME]);
  return scheme + "://" + window.location.host + "/static/content.json";
}

async function get_descript(url, name) {
  safeUrl = await buildUrl(url);
  resp = await fetch(safeUrl);
  return (await resp.json()).find((x) => x.name == name);
}

document.addEventListener("DOMContentLoaded", function () {
  get_descript(eleUrl.innerText, eleName.innerText).then((data) => {
    displayTitle.innerText = data.name;
    displayDescript.innerHTML = data.descript;
  });
});
