document.addEventListener("DOMContentLoaded", () => {
    const injectScript = async (command) => {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (cmd) => {
          window.igScraperCommand = cmd;
          if (typeof window.runIgScraper === 'function') {
            window.runIgScraper(cmd);
          }
        },
        args: [command]
      });
  
      if (command === 'start') {
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ["content.js"]
        });
      }
    };
  
    document.getElementById("start").addEventListener("click", () => injectScript("start"));
    document.getElementById("stop").addEventListener("click", () => injectScript("stop"));
  });
  