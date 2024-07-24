ComponentIndex = {
  SCHEME: 1,
  USER_INFO: 2,
  DOMAIN: 3,
  PORT: 4,
  PATH: 5,
  QUERY_DATA: 6,
  FRAGMENT: 7,
};

async function validate(url) {
  splitRe_ = RegExp(
    "^(?:([^:/?#.]+):)?(?://(?:([^/#?/?#]*)@)?([^/#?]*?)(?::([0-9]+))?(?=[/\\\\#?]|$))?([^?#]+)?(?:\\?([^#]*))?(?:#([\\s\\S]*))?$",
  );
  tmp = url.match(splitRe_);
  domain = tmp[ComponentIndex.DOMAIN];
  scheme = tmp[ComponentIndex.SCHEME];
  if (domain !== window.location.hostname) throw "invalid host";
  if (scheme !== "http" && scheme !== "https") throw "invalid scheme";
}

async function get_descript(url, name) {
  await validate(url);
  resp = await fetch(url);
  return (await resp.json()).find((x) => x.name == name);
}

document.addEventListener("DOMContentLoaded", function () {
  get_descript(eleUrl.innerText, eleName.innerText).then((data) => {
    displayTitle.innerText = data.name;
    displayDescript.innerHTML = data.descript;
  });
});
