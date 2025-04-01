(function extractAndDownloadLinks() {
    const anchors = document.querySelectorAll('a[href^="/p/"]');
    const links = new Set();
  
    anchors.forEach(a => {
      const href = a.getAttribute("href");
      if (/^\/p\/[A-Za-z0-9_-]+\/?$/.test(href)) {
        links.add(`https://www.instagram.com${href}`);
      }
    });
  
    if (links.size === 0) {
      alert("No video links found.");
      return;
    }
  
    const blob = new Blob([Array.from(links).join("\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "video_links.txt";
    a.click();
    URL.revokeObjectURL(url);
  })();
  