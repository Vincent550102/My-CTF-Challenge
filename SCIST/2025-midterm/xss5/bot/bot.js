const puppeteer = require("puppeteer");

const FLAG = process.env.FLAG || "test{flag}";

const sleep = async (s) =>
  new Promise((resolve) => setTimeout(resolve, 1000 * s));

const visit = async (url) => {
  let browser;
  try {
    browser = await puppeteer.launch({
      headless: true,
      args: ["--disable-gpu", "--no-sandbox"],
      executablePath: "/usr/bin/chromium-browser",
    });
    const context = await browser.createIncognitoBrowserContext();
    const page = await context.newPage();
    await sleep(1);
    await page.setCookie({ name: "flag", value: FLAG, domain: "xss5" });
    await sleep(1);
    page.goto(url);
    await sleep(3);

    await browser.close();
  } catch (e) {
    console.log(e);
  } finally {
    if (browser) await browser.close();
  }
};

module.exports = visit;

if (require.main === module) {
  visit("http://example.com");
}
