const puppeteer = require("puppeteer");

const FLAG = process.env.FLAG || "TSC{example_flag}";
const SITE_URL = process.env.SITE_URL || "http://world/";

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

    // create flag cookie, you need to steal it!
    const page = await context.newPage();
    await sleep(1);
    await page.setCookie({ name: "flag", value: FLAG, domain: "world" });
    await sleep(1);
    await page.goto(url, { waitUntil: "networkidle0" });
    await sleep(5);
    await page.close();
  } catch (e) {
    console.log(e);
  } finally {
    if (browser) await browser.close();
  }
};

module.exports = visit;
