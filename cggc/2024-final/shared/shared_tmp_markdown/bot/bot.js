const puppeteer = require("puppeteer");

const FLAG = process.env.FLAG || "CGGC{fakeflag}";
const SITE_URL = process.env.SITE_URL || "http://markdown/";

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

    // create flag
    const createFlag = await context.newPage();
    await createFlag.goto(SITE_URL, { waitUntil: "networkidle0" });
    await createFlag.waitForSelector("#note");
    await createFlag.type("#note", FLAG);
    await createFlag.waitForSelector("#submit");
    await createFlag.click("#submit");
    await sleep(1);
    await createFlag.close();

    // visit given url
    const page = await context.newPage();
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
