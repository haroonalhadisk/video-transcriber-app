(() => {
    let isScrolling = false;
    let seenLinks = new Set();
  
    async function autoScrollAndCollect() {
      isScrolling = true;
  
      while (isScrolling) {
        const newLinks = [...document.querySelectorAll('a[href^="/p/"]')]
          .map(a => a.getAttribute("href"))
          .filter(href => /^\/p\/[A-Za-z0-9_-]+\/?$/.test(href))
          .map(href => `https://www.instagram.com${href}`);
  
        newLinks.forEach(link => seenLinks.add(link));
  
        window.scrollBy(0, window.innerHeight);
        await new Promise(resolve => setTimeout(resolve, 1200));
      }
  
      if (seenLinks.size > 0) {
        const blob = new Blob([Array.from(seenLinks).join("\n")], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "video_links.txt";
        a.click();
        URL.revokeObjectURL(url);
      } else {
        alert("No links found.");
      }
    }
  
    window.runIgScraper = (command) => {
      if (command === "start") {
        if (!isScrolling) {
          seenLinks.clear();
          autoScrollAndCollect();
        }
      } else if (command === "stop") {
        isScrolling = false;
      }
    };
  
    if (typeof window.igScraperCommand !== "undefined") {
      window.runIgScraper(window.igScraperCommand);
    }
  })();
  